import os

import argparse

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.ml.feature import IDF, Tokenizer
from pyspark.ml.feature import StringIndexer
from pyspark.ml.feature import CountVectorizer
from pyspark.ml import Pipeline, PipelineModel
from ssp.utils import ConfigManager, print_info
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import NGram, VectorAssembler


# https://github.com/tthustla/setiment_analysis_pyspark/blob/master/Sentiment%20Analysis%20with%20PySpark.ipynb
class SentimentSparkModel(object):
    def __init__(self, config_file_path, spark=None):
        self._config = ConfigManager(config_path=config_file_path)
        if spark:
            self._spark = spark
        else:
            self._spark_master = self._config.get_item("spark", "master")
            self._spark = SparkSession.builder. \
                appName("twitter_stream"). \
                config("spark.sql.warehouse.dir", self._warehouse_location). \
                master(self._spark_master). \
                enableHiveSupport(). \
                getOrCreate()

        self._spark.sparkContext.setLogLevel("error")
        self._pipeline = None

        self._twitter_dataset = self._config.get_item("dataset", "twitter_dataset")
        self._model_path = self._config.get_item("sentiment_model", "store_path")
        self._warehouse_location = self._config.get_item("spark", "warehouse_location")

        self._twitter_dataset_schema = StructType([
            StructField("target", StringType(), False),
            StructField("id", StringType(), False),
            StructField("date", StringType(), False),
            StructField("flag", StringType(), False),
            StructField("user", StringType(), False),
            StructField("text", StringType(), False)
        ])

        if os.path.exists(self._model_path):
            self._model = PipelineModel.load(self._model_path)
        else:
            self._model = None

    def prepare_data(self):
        df = self._spark.read.csv(self._twitter_dataset, schema=self._twitter_dataset_schema)
        self._train_df, self._val_df, self._test_df = df.randomSplit([0.8, 0.1, 0.1])
        print_info("Train data count : {}".format(self._train_df.count()))
        print_info("Val data count : {}".format(self._val_df.count()))
        print_info("Test data count : {}".format(self._test_df.count()))

    def build_naive_pipeline(self, input_col="text"):
        # Tokenize the text
        tokenizer = Tokenizer(inputCol=input_col, outputCol="words")
        # Count each word and use the count as its weight
        cv = CountVectorizer(vocabSize=2**16, inputCol="words", outputCol='tf')
        # IDF
        idf = IDF(inputCol='tf', outputCol="features", minDocFreq=5)  # minDocFreq: remove sparse terms
        label_string_idx = StringIndexer(inputCol="target", outputCol="label")
        lr = LogisticRegression(maxIter=100)
        self._pipeline = Pipeline(stages=[tokenizer, cv, idf, label_string_idx, lr])

    def build_ngrams_wocs(self, inputCol="text", outputCol="target", n=3):
        tokenizer = [Tokenizer(inputCol=inputCol, outputCol="words")]
        ngrams = [
            NGram(n=i, inputCol="words", outputCol="{0}_grams".format(i))
            for i in range(1, n + 1)
        ]

        cv = [
            CountVectorizer(vocabSize=5460, inputCol="{0}_grams".format(i),
                            outputCol="{0}_tf".format(i))
            for i in range(1, n + 1)
        ]
        idf = [IDF(inputCol="{0}_tf".format(i), outputCol="{0}_tfidf".format(i), minDocFreq=5) for i in range(1, n + 1)]

        assembler = [VectorAssembler(
            inputCols=["{0}_tfidf".format(i) for i in range(1, n + 1)],
            outputCol="features"
        )]
        label_stringIdx = [StringIndexer(inputCol=outputCol, outputCol="label")]
        lr = [LogisticRegression(maxIter=100)]
        return Pipeline(stages=tokenizer + ngrams + cv + idf + assembler + label_stringIdx + lr)

    def train(self):
        self.prepare_data()
        pipeline = self.build_ngrams_wocs()
        self._model = pipeline.fit(self._train_df)
        self._model.write().overwrite().save(self._model_path)
        return self._model

    def evaluate(self, model):
        # evaluator = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction")
        predictions = model.transform(self._val_df)
        accuracy = predictions.filter(predictions.label == predictions.prediction).count() / float(predictions.count())
        print_info("Accuracy : {}".format(accuracy))

    def predict(self, df):
        predicted_df = self._model.transform(df)
        return predicted_df



if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config.ini",
                          required=False,
                          help="File path of config.ini")

    parsed_args = optparse.parse_args()

    model = SentimentSparkModel(config_file_path=parsed_args.config_file)
    spark_model = model.train()
    model.evaluate(model=spark_model)


