#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import gin
from pyspark.sql.functions import udf, col, explode
from pyspark.sql.types import ArrayType, StringType
from ssp.spark.streaming.common.twitter_streamer_base import TwitterStreamerBase


def extract_hashtag(text):
    """
    Extracts the twitter #hashtag from the text
    :param text: (str) Twitter text
    :return: (list) List of hashtags
    """
    if text is not None:
        text = text.replace('\n', ' ').replace('\r', '')
        text = text.split(" ")
        text = [word for word in text if "#" in word]
        if len(text) == 0:
            text = ["no tags"]
    else:
        text = ["no tags"]
    return text

extract_hashtag_udf = udf(extract_hashtag, ArrayType(StringType()))

@gin.configurable
class TrendingHashTags(TwitterStreamerBase):
    """
    Extracts hash tags and counts the individual occurrence of tags.
    And then dumps the data into a Postgresql Database table

    :param kafka_bootstrap_servers: (str) host_url:port
    :param kafka_topic: (str) Live stream Kafka topic
    :param checkpoint_dir: (str) Spark Streaming checkpoint directory
    :param bronze_parquet_dir: (str) Input stream directory path. For local paths prefix it with "file///"
    :param warehouse_location: (str) Spark warehouse location
    :param spark_master: (str) Spark master url
    :param postgresql_host: (str) Postgresql host url
    :param postgresql_port: (str) Postgres port
    :param postgresql_database: (str) Database name
    :param postgresql_user: (str) Postgresql user name
    :param postgresql_password: (str) Postgresql user password
    :param processing_time: (str) Spark Streaming process interval
    :param is_live_stream: (bool) Use live stream or to use streamed directory as input
    """

    def __init__(self,
                 kafka_bootstrap_servers="localhost:9092",
                 kafka_topic="ai_tweets_topic",
                 checkpoint_dir="hdfs://localhost:9000/tmp/ssp/data/lake/checkpoint/",
                 bronze_parquet_dir="hdfs://localhost:9000/tmp/ssp/data/lake/bronze/",
                 warehouse_location="/opt/spark-warehouse/",
                 spark_master="spark://IMCHLT304:7077",
                 postgresql_host="localhost",
                 postgresql_port="5432",
                 postgresql_database="sparkstreamingdb",
                 postgresql_user="sparkstreaming",
                 postgresql_password="sparkstreaming",
                 processing_time='5 seconds',
                 is_live_stream=True):

        TwitterStreamerBase.__init__(self,
                                     spark_master=spark_master,
                                     checkpoint_dir=checkpoint_dir,
                                     warehouse_location=warehouse_location,
                                     kafka_bootstrap_servers=kafka_bootstrap_servers,
                                     kafka_topic=kafka_topic,
                                     processing_time=processing_time)

        self._bronze_parquet_dir = bronze_parquet_dir
        self.spark = self._get_spark()
        self.spark.sparkContext.setLogLevel("DEBUG")

        self._postgresql_host = postgresql_host
        self._postgresql_port = postgresql_port
        self._postgresql_database = postgresql_database
        self._postgresql_user = postgresql_user
        self._postgresql_password = postgresql_password

        self._is_live_stream = is_live_stream

    def _online_process(self):
        tweet_stream = self._get_source_stream()
        return tweet_stream

    def _hdfs_process(self):
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
            tweet_stream = self._online_process()
        else:
            tweet_stream = self._hdfs_process()

        tweet_stream.printSchema()

        tweet_stream = tweet_stream. \
            withColumn("hashtag", explode(extract_hashtag_udf(col("text")))). \
            groupBy("hashtag").count().sort(col("count").desc())

        def foreach_batch_function(df, epoch_id):
            # Transform and write batchDF
            df.printSchema()
            df.show(50, False)

            # TODO closure in effect, consider refactoring
            mode = "overwrite"
            url = "jdbc:postgresql://{}:{}/{}".format(self._postgresql_host,
                                                      self._postgresql_port,
                                                      self._postgresql_database)
            properties = {"user": self._postgresql_user,
                          "password": self._postgresql_password,
                          "driver": "org.postgresql.Driver"}
            # url = "jdbc:postgresql://localhost:5432/sparkstreamingdb"
            # properties = {"user": "sparkstreaming", "password": "sparkstreaming", "driver": "org.postgresql.Driver"}
            df.write.jdbc(url=url, table="trending_hashtags", mode=mode, properties=properties)


        tweet_stream.writeStream.outputMode("complete").foreachBatch(foreach_batch_function).start().awaitTermination()
