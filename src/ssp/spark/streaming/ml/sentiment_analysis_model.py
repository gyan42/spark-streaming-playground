#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import os

import pyarrow as pa
import gin
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.ml.feature import IDF, Tokenizer
from pyspark.ml.feature import StringIndexer
from pyspark.ml.feature import CountVectorizer
from pyspark.ml import Pipeline, PipelineModel
from ssp.logger.pretty_print import print_info
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import NGram, VectorAssembler


# https://github.com/tthustla/setiment_analysis_pyspark/blob/master/Sentiment%20Analysis%20with%20PySpark.ipynb
@gin.configurable
class SentimentSparkModel(object):
    """
    Build text classification model for tweet sentiment classification
    If HDFS details are given, model will be stored in HDFS

    :param spark: Sparksession
    :param spark_master: Spark master URL
    :param sentiment_dataset_path: Tweeter Kaggle sentiment dataset path
    :param model_dir: Model sava directory
    :param hdfs_host: HDFS host url
    :param hdfs_port: HDFS port
    """

    def __init__(self,
                 spark=None,
                 spark_master="spark://IMCHLT276:7077",
                 sentiment_dataset_path="data/dataset/sentiment140/",
                 model_dir="~/ssp/data/model/sentiment/",
                 hdfs_host=None,
                 hdfs_port=None):

        self._spark_master = spark_master

        self._model_dir = os.path.expanduser(model_dir)

        self._hdfs_host, self._hdfs_port = hdfs_host, hdfs_port

        if hdfs_host and hdfs_port:
            self._hdfs_fs = pa.hdfs.connect(hdfs_host, hdfs_port)
            self._is_local_dir = False

            if self._hdfs_fs.exists(self._model_dir):
                self._pre_trained = True
                print_info(f"Loading model...{self._model_dir}")
                self._model = PipelineModel.load(self._model_dir)
            else:
                self._model = None
        else:
            self._is_local_dir = True
            if os.path.exists(self._model_dir):
                self._model = PipelineModel.load(self._model_dir)
            else:
                self._model = None

        if spark:
            self._spark = spark
        else:
            self._spark = SparkSession.builder. \
                appName("twitter_stream"). \
                master(self._spark_master). \
                enableHiveSupport(). \
                getOrCreate()

        self._spark.sparkContext.setLogLevel("error")
        self._pipeline = None

        self._ai_tweets_topicset_path = "file:///" + os.path.abspath(sentiment_dataset_path)

        self._ai_tweets_topicset_schema = StructType([
            StructField("target", StringType(), False),
            StructField("id", StringType(), False),
            StructField("date", StringType(), False),
            StructField("flag", StringType(), False),
            StructField("user", StringType(), False),
            StructField("text", StringType(), False)
        ])

        self._train_df, self._val_df, self._test_df = None, None, None

    def prepare_data(self):
        df = self._spark.read.csv(self._ai_tweets_topicset_path, schema=self._ai_tweets_topicset_schema)
        self._train_df, self._val_df, self._test_df = df.randomSplit([0.8, 0.1, 0.1])
        print_info("Train data count : {}".format(self._train_df.count()))
        print_info("Val data count : {}".format(self._val_df.count()))
        print_info("Test data count : {}".format(self._test_df.count()))

    def build_naive_pipeline(self, input_col="text"):
        # Tokenize the text
        tokenizer = Tokenizer(inputCol=input_col, outputCol="words")
        # Count each word and use the count as its weight
        cv = CountVectorizer(vocabSize=2 ** 16, inputCol="words", outputCol='tf')
        # IDF
        idf = IDF(inputCol='tf', outputCol="features", minDocFreq=5)  # minDocFreq: remove sparse terms
        label_string_idx = StringIndexer(inputCol="target", outputCol="label")
        lr = LogisticRegression(maxIter=100)
        self._pipeline = Pipeline(stages=[tokenizer, cv, idf, label_string_idx, lr])

    def build_ngrams_wocs(self, inputcol="text", outputcol="target", n=3):
        tokenizer = [Tokenizer(inputCol=inputcol, outputCol="words")]
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
        label_stringIdx = [StringIndexer(inputCol=outputcol, outputCol="label")]
        lr = [LogisticRegression(maxIter=100)]
        return Pipeline(stages=tokenizer + ngrams + cv + idf + assembler + label_stringIdx + lr)

    def train(self):
        self.prepare_data()
        pipeline = self.build_ngrams_wocs()
        print_info(self._train_df.show())
        self._model = pipeline.fit(self._train_df)
        # TODO
        self._model.write().overwrite().save(self._model_dir)
        return self._model

    def evaluate(self, model):
        # evaluator = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction")
        predictions = model.transform(self._val_df)
        accuracy = predictions.filter(predictions.label == predictions.prediction).count() / float(predictions.count())
        print_info("Accuracy : {}".format(accuracy))

    def predict(self, df):
        predicted_df = self._model.transform(df)
        return predicted_df

