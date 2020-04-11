import argparse
import gin
from pyspark.sql import SparkSession

from ssp.spark.streaming.common.twitter_streamer_base import TwitterStreamerBase
from ssp.spark.streaming.ml.sentiment_analysis_model_main import SentimentSparkModel
# from ssp.customudf.textblob_sentiment import textblob_sentiment_analysis_udf

@gin.configurable
class SentimentAnalysis(TwitterStreamerBase):
    def __init__(self,
                 kafka_bootstrap_servers="localhost:9092",
                 kafka_topic="ai_tweets_topic",
                 checkpoint_dir="hdfs://localhost:9000/tmp/ssp/data/lake/checkpoint/",
                 parquet_dir="hdfs://localhost:9000/tmp/ssp/data/lake/silver/",
                 warehouse_location="/opt/spark-warehouse/",
                 spark_master="spark://IMCHLT276:7077",
                 is_live_stream=True,
                 processing_time='5 seconds'):

        TwitterStreamerBase.__init__(self,
                                     spark_master=spark_master,
                                     checkpoint_dir=checkpoint_dir,
                                     warehouse_location=warehouse_location,
                                     kafka_bootstrap_servers=kafka_bootstrap_servers,
                                     kafka_topic=kafka_topic,
                                     processing_time=processing_time)
        self._spark_master = spark_master

        self._checkpoint_dir = checkpoint_dir
        self._parquet_dir = parquet_dir
        self._warehouse_location = warehouse_location

        self.spark = SparkSession.builder. \
            appName("twitter_stream"). \
            master(self._spark_master). \
            config("spark.sql.warehouse.dir", self._warehouse_location). \
            config("spark.sql.streaming.checkpointLocation", self._checkpoint_dir). \
            enableHiveSupport(). \
            getOrCreate()

        self.spark.sparkContext.setLogLevel("error")

        self._model = SentimentSparkModel(spark=self.spark)

        self._is_live_stream = is_live_stream


    def online_process(self):
        tweet_stream = self.get_source_stream()
        return tweet_stream

    def hdfs_process(self):
        userSchema = self.spark.read.parquet(self._bronze_parquet_dir).schema
        tweet_stream = self.spark.readStream. \
            schema(userSchema).\
            format("parquet"). \
            option("ignoreChanges", "true"). \
            option("failOnDataLoss", "false"). \
            load(self._bronze_parquet_dir)

        return tweet_stream

    def process(self):
        if self._is_live_stream:
            tweet_stream = self.online_process()
        else:
            tweet_stream = self.hdfs_process()


        def foreach_batch_function(df, epoch_id):
            # Transform and write batchDF
            df = self._model.predict(df).select(["text", "prediction"])
            # df = df.withColumn("sentiment", textblob_sentiment_analysis_udf("text"))
            df.show(50, False)

        tweet_stream.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()