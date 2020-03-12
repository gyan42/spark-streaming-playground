import argparse
import os
import shutil

from tweepy.auth import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
# import socket
from kafka import KafkaProducer
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, regexp_replace
from pyspark.sql.types import StructType, StringType, IntegerType

from ssp.utils.config_manager import ConfigManager, print_info
from ssp.utils.configuration import StreamingConfigs


def check_n_mk_dirs(path, is_remove=False):
    if os.path.exists(path):
        if is_remove:
            shutil.rmtree(path)
    else:
        os.makedirs(path)


# we create this class that inherits from the StreamListener in tweepy StreamListener
class TweetsListener(StreamListener):
    def __init__(self, kafka_addr='localhost:9092', topic='twitter_data'):
        StreamListener.__init__(self)
        # Kafka settings
        self._kafka_producer = KafkaProducer(bootstrap_servers=kafka_addr)
        self._kafka_topic = topic

    def on_data(self, data):
        print_info(data)
        self._kafka_producer.send(self._kafka_topic, data.encode('utf-8')).get(timeout=10)
        return True

    def if_error(self, status):
        print(status)
        return True

class TwitterDataset(StreamingConfigs):
    """
    Twitter ingestion class
    - Gets the twitter stream data and dumps the data into Kafka topic
    - Starts the Spark Structured Streaming against the Kafka topic and dumps the data to HDFS
    """
    def __init__(self, config_file_path):
        StreamingConfigs.__init__(self, config_file_path=config_file_path)
        self._config = ConfigManager(config_path=config_file_path)

        check_n_mk_dirs(self._checkpoint_dir, is_remove=self._remove_old_data)
        check_n_mk_dirs(self._bronze_parquet_dir, is_remove=self._remove_old_data)

    def twitter_socket_stream(self):
        auth = OAuthHandler(self._twitter_consumer_key, self._twitter_consumer_secret)
        auth.set_access_token(self._twitter_access_token, self._twitter_access_secret)

        twitter_stream = Stream(auth, TweetsListener(kafka_addr=self._kafka_addr, topic=self._kafka_topic))
        twitter_stream.filter(track=["india"])  # this is the topic we are interested in

    def structured_streaming(self):
        # get spark session
        spark = SparkSession.builder. \
            appName("TwitterRawDataIngestion"). \
            master(self._spark_master). \
            config("spark.sql.streaming.checkpointLocation", self._checkpoint_dir). \
            config("spark.sql.warehouse.dir", self._warehouse_location). \
            enableHiveSupport(). \
            getOrCreate()

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

        # define the schema we wanted
        schema = StructType(). \
            add('created_at', StringType(), False). \
            add('source', StringType(), False). \
            add('text', StringType(), False). \
            add('geo', StringType(), True). \
            add('retweet_count', IntegerType(), True)

        # extract the data as per our schema
        tweet_df = tweet_stream. \
            selectExpr("cast (value as STRING)"). \
            select(from_json("value", schema).
                   alias("temp")). \
            select("temp.*"). \
            withColumn("source", regexp_replace("source", "<[^>]*>", ""))


        #tweet_df.createGlobalTempView("raw_tweet_df")

        # dump the data into bronze lake path
        storeDF = tweet_df.writeStream. \
            format("parquet"). \
            outputMode("append"). \
            option("path", self._bronze_parquet_dir). \
            option("checkpointLocation", self._checkpoint_dir). \
            trigger(processingTime='10 seconds'). \
            start()

        spark.streams.awaitAnyTermination()

if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config.ini",
                          required=False,
                          help="File path of config.ini")

    optparse.add_argument("-m", "--mode",
                          required=True,
                          help="[start_tweet_stream, structured_streaming]")

    parsed_args = optparse.parse_args()

    dataset = TwitterDataset(config_file_path=parsed_args.config_file)

    if parsed_args.mode == "start_tweet_stream":
        dataset.twitter_socket_stream()
    elif parsed_args.mode == "structured_streaming":
        dataset.structured_streaming()
    else:
        raise RuntimeError("Invalid choice")
