from pyspark.sql import SparkSession

import re

from ssp.logger.pretty_print import print_error, print_info
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

"""
When it comes to describing the semantics of a delivery mechanism, there are three basic categories:

    at-most-once delivery means that for each message handed to the mechanism, that message is delivered once or not at all; in more casual terms it means that messages may be lost.
    at-least-once delivery means that for each message handed to the mechanism potentially multiple attempts are made at delivering it, such that at least one succeeds; again, in more casual terms this means that messages may be duplicated but not lost.
    exactly-once delivery means that for each message handed to the mechanism exactly one delivery is made to the recipient; the message can neither be lost nor duplicated.

The first one is the cheapest—highest performance, least implementation overhead—because it can be done in a fire-and-forget fashion without keeping state at the sending end or in the transport mechanism. The second one requires retries to counter transport losses, which means keeping state at the sending end and having an acknowledgement mechanism at the receiving end. The third is most expensive—and has consequently worst performance—because in addition to the second it requires state to be kept at the receiving end in order to filter out duplicate deliveries.

"""

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

    def get_source_stream(self, kafka_topic="mix_tweets_topic"):

        print_info("\n\n------------------------------------------------------------------------------------------\n\n")
        print_info(f"\t\t\t Kafka topis is {kafka_topic}")
        print_info("\n\n------------------------------------------------------------------------------------------\n\n")

        spark = self.get_spark()

        # read the tweets from kafka topic
        tweet_stream = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self._kafka_bootstrap_servers) \
            .option("subscribe", kafka_topic) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()

        tweet_stream.printSchema()

        # converts the incoming data to string
        # parses the data with inbuild Json parser
        # extract the data as per our schema
        # cleans the html tags
        # extracts the `text` from the tweets
        # creates hash column
        # filer out null id columns
        # watermark : how late data can arrive and get considered for aggregation
        # processing time : how often to emt update, generally handled at writestream side
        tweet_df = tweet_stream. \
            selectExpr("cast (value as STRING)"). \
            select(from_json("value", TwitterStreamerBase.get_schema()).
                   alias("tweet")). \
            select(col("tweet.id_str"),
                   col("tweet.created_at"),
                   col("tweet.source"),
                   col("tweet.text"),
                   col("tweet.extended_tweet.full_text").alias("etext"),
                   col("tweet.retweeted_status.extended_tweet.full_text").alias("rtext"),
                   col("tweet.entities.urls.expanded_url"),
                   col("tweet.entities.media.media_url_https")). \
            withColumn("source", regexp_replace("source", "<[^>]*>", "")). \
            withColumn("text", pick_text_udf(col("text"), col("rtext"), col("etext"))). \
            withColumn("hash", sha2("text", 256)). \
            drop("rtext", "etext"). \
            where(~isnull(col("id_str")))
            # TODO https://stackoverflow.com/questions/45474270/how-to-expire-state-of-dropduplicates-in-structured-streaming-to-avoid-oom
            # withWatermark("timestamp", "10 minutes"). \
            # dropDuplicates("id_str")

        return tweet_df