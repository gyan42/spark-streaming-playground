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
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col

from ssp.logger.pretty_print import print_error
from ssp.spark.streaming.common.twitter_streamer_base import TwitterStreamerBase
from ssp.spark.udf.tensorflow_serving_api_udf import get_text_classifier_udf


@gin.configurable
class SreamingTextClassifier(TwitterStreamerBase):
    def __init__(self,
                 kafka_bootstrap_servers="localhost:9092",
                 kafka_topic="ai_tweets_topic",
                 checkpoint_dir="hdfs://localhost:9000/tmp/ssp/data/lake/checkpoint/",
                 bronze_parquet_dir="hdfs://localhost:9000/tmp/ssp/data/lake/bronze/",
                 warehouse_location="/opt/spark-warehouse/",
                 spark_master="spark://IMCHLT276:7077",
                 postgresql_host="localhost",
                 postgresql_port="5432",
                 postgresql_database="sparkstreamingdb",
                 postgresql_user="sparkstreaming",
                 postgresql_password="sparkstreaming",
                 processing_time='5 seconds',
                 tokenizer_path=gin.REQUIRED,
                 is_live_stream=True,
                 is_docker=False):

        TwitterStreamerBase.__init__(self,
                                     spark_master=spark_master,
                                     checkpoint_dir=checkpoint_dir,
                                     warehouse_location=warehouse_location,
                                     kafka_bootstrap_servers=kafka_bootstrap_servers,
                                     kafka_topic=kafka_topic,
                                     processing_time=processing_time)


        self._spark_master = spark_master

        self._checkpoint_dir = checkpoint_dir
        self._bronze_parquet_dir = bronze_parquet_dir
        self._warehouse_location = warehouse_location

        self._postgresql_host = postgresql_host
        self._postgresql_port = postgresql_port
        self._postgresql_database = postgresql_database
        self._postgresql_user = postgresql_user
        self._postgresql_password = postgresql_password

        self.spark = SparkSession.builder. \
            appName("twitter_stream"). \
            master(self._spark_master). \
            config("spark.sql.streaming.checkpointLocation", self._checkpoint_dir). \
            getOrCreate()

        self.spark.sparkContext.setLogLevel("error")

        self._tokenizer_path = tokenizer_path
        self._is_live_stream = is_live_stream
        self._is_docker = is_docker

    def online_process(self):
        tweet_stream = self._get_source_stream()
        return tweet_stream

    def hdfs_process(self):
        userSchema = self.spark.read.parquet(self._bronze_parquet_dir).schema

        tweet_stream = self.spark.readStream. \
            schema(userSchema). \
            format("parquet"). \
            option("ignoreChanges", "true"). \
            load(self._bronze_parquet_dir)
        return tweet_stream

    def process(self):
        if self._is_live_stream:
            tweet_stream = self.online_process()
        else:
            tweet_stream = self.hdfs_process()

        # Note: UDF with wrapper for different URL based on from where the code is triggered docker/local machine
        text_clsfier = get_text_classifier_udf(is_docker=self._is_docker, tokenizer_path=self._tokenizer_path)
        tweet_stream.printSchema()
        tweet_stream = tweet_stream. \
            withColumn("ai_prob", text_clsfier(col("text"))). \
            where(col("ai_prob") > 0.5)

        def foreach_batch_function(df, epoch_id):
            # Transform and write batchDF
            df.printSchema()
            df.select(["text", "ai_prob"]).show(50, False)

            mode = "append"
            url = "jdbc:postgresql://{}:{}/{}".format(self._postgresql_host,
                                                      self._postgresql_port,
                                                      self._postgresql_database)
            properties = {"user": self._postgresql_user,
                          "password": self._postgresql_password,
                          "driver": "org.postgresql.Driver"}
            df.write.jdbc(url=url, table="ai_tweets", mode=mode, properties=properties)

        tweet_stream.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()

