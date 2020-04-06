from pyspark.sql import SparkSession

import re

from ssp.logger.pretty_print import print_error
from ssp.spark.streaming.common.streamer_base import StreamerBase
from pyspark.sql.types import StructType, StringType, IntegerType, ArrayType
from pyspark.sql.functions import col, isnull
from pyspark.sql.functions import sha2, udf
from pyspark.sql.functions import from_json, regexp_replace

def pick_text(text, rtext, etext):
    ret = ""
    if etext:
        ret = etext
    elif rtext:
        ret = rtext
    elif text:
        ret = text
    else:
        ret = ""

    return re.sub("\n|\r", "", ret).strip()


pick_text_udf = udf(pick_text, StringType())


class TwitterStreamerBase(StreamerBase):
    def __init__(self,
                 spark_master,
                 checkpoint_dir,
                 warehouse_location,
                 kafka_bootstrap_servers,
                 kafka_topic,
                 processing_time='5 seconds'):
        StreamerBase.__init__(self,
                              spark_master=spark_master,
                              checkpoint_dir=checkpoint_dir,
                              warehouse_location=warehouse_location,
                              kafka_bootstrap_servers=kafka_bootstrap_servers,
                              kafka_topic=kafka_topic,
                              processing_time=processing_time)

    @staticmethod
    def get_schema():
        # define the schema to extract the data we are interested
        # https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object
        urls = ArrayType(StructType(). \
                         add("expanded_url", StringType(), True))

        media = ArrayType(StructType(). \
                          add("media_url", StringType(), True). \
                          add("media_url_https", StringType(), True))

        # Tweet -> Entities{} -> Urls[] -> Media[]
        entities = StructType(). \
            add("urls", urls, True). \
            add("media", media)

        schema = StructType(). \
            add('id_str', StringType(), False). \
            add('created_at', StringType(), False). \
            add('source', StringType(), False). \
            add('text', StringType(), False). \
            add('extended_tweet', StructType().add("full_text", StringType(), True), True). \
            add('entities', entities, False). \
            add('retweeted_status', StructType().add('extended_tweet', StructType().add("full_text", StringType(), True), True).add('user', StructType().add('description', StringType())), True). \
            add('geo', StringType(), True). \
            add('retweet_count', IntegerType(), True)

        return schema

    def get_source_stream(self):
        spark = self.get_spark()

        print_error(f"{self._kafka_topic}, {self._kafka_bootstrap_servers}")
        # read the tweets from kafka topic
        tweet_stream = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self._kafka_bootstrap_servers) \
            .option("subscribe", self._kafka_topic) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()

        tweet_stream.printSchema()

        # extract the data as per our schema
        tweet_df = tweet_stream. \
            selectExpr("cast (value as STRING)"). \
            select(from_json("value", TwitterStreamerBase.get_schema()).
                   alias("temp")). \
            select(col("temp.id_str"),
                   col("temp.created_at"),
                   col("temp.source"),
                   col("temp.text"),
                   col("temp.extended_tweet.full_text").alias("etext"),
                   col("temp.retweeted_status.extended_tweet.full_text").alias("rtext"),
                   col("temp.entities.urls.expanded_url"),
                   col("temp.entities.media.media_url_https")). \
            withColumn("source", regexp_replace("source", "<[^>]*>", "")). \
            withColumn("text", pick_text_udf(col("text"), col("rtext"), col("etext"))). \
            withColumn("hash", sha2("text", 256)). \
            drop("rtext", "etext"). \
            where(~isnull(col("id_str")))

        return tweet_df