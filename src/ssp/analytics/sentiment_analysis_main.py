import argparse
from pyspark.sql import SparkSession

from ssp.ml.sentiment_analysis_model_main import SentimentSparkModel
from ssp.utils import ConfigManager

from ssp.customudf.textblob_sentiment import textblob_sentiment_analysis_udf


class SentimentAnalysis(object):
    def __init__(self, config_file_path):
        self._config = ConfigManager(config_path=config_file_path)

        self._spark_master = self._config.get_item("spark", "master")

        self._checkpoint_dir = self._config.get_item("dataset", "checkpoint_dir")
        self._parquet_dir = self._config.get_item("dataset", "silver_parquet_dir")
        self._warehouse_location = self._config.get_item("spark", "warehouse_location")


        self.spark = SparkSession.builder. \
            appName("twitter_stream"). \
            master(self._spark_master). \
            config("spark.sql.warehouse.dir", self._warehouse_location). \
            config("spark.sql.streaming.checkpointLocation", self._checkpoint_dir). \
            enableHiveSupport(). \
            getOrCreate()

        self.spark.sparkContext.setLogLevel("error")

        self._model = SentimentSparkModel(config_file_path=config_file_path, spark=self.spark)

    def process(self):
        tweet_table_stream = self.spark.readStream. \
            format("delta"). \
            option("ignoreChanges", "true"). \
            load(self._parquet_dir)

        def foreach_batch_function(df, epoch_id):
            # Transform and write batchDF
            df = self._model.predict(df).select(["text", "prediction"])
            df = df.withColumn("sentiment", textblob_sentiment_analysis_udf("text"))
            df.show(50, False)

        tweet_table_stream.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()


if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark SentimentAnalysis pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config.ini",
                          required=False,
                          help="File path of config.ini")

    parsed_args = optparse.parse_args()

    nlp_processing = SentimentAnalysis(config_file_path=parsed_args.config_file)

    nlp_processing.process()
