import argparse
import os
import shutil
from threading import Thread, Event
from tweepy.auth import OAuthHandler
from tweepy.streaming import Stream, StreamListener
from tweepy.streaming import StreamListener

import pandas as pd
import glob

# import socket
from kafka import KafkaProducer
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, regexp_replace
from pyspark.sql.types import StructType, StringType, IntegerType

from ssp.utils.config_manager import ConfigManager, print_info
from ssp.utils.configuration import StreamingConfigs

NATURE_KEYWORDS = ["nature", "life", "climate", "animal", "human", "weather", "earth",
                    "ocean", "sea", "wildlife", "fungus", "virus", "algae", "bacteria",
                    "World", "oxygen", "river", "water", "land", "north pole", "south pole",
                   "species", "natural", "mammals", "living", "organism", "fish"]

SPACE_KEYWORDS = ["space", "universe", " nasa", "star", "solar system", "sun", "moon",
                  "time", "cosmos", "big bang", "gravity", "energy", "dimension", "matter",
                  "radiation", "electromagnetic", "proton", "electron", "cosmology", "physics"]

ML_KEYWORDS = ["machine learning", "ml", "dl", "deep learning", "learning", "classification",
               "clustering", "regression", "svm", "neural networks", "tensorflow", "pytorch",
               "ai", "artificial", "intelligence", "algorithms", "rl"]


def check_n_mk_dirs(path, is_remove=False):
    if os.path.exists(path):
        if is_remove:
            shutil.rmtree(path)
    else:
        os.makedirs(path)


# http://docs.tweepy.org/en/latest/streaming_how_to.html
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

def get_raw_dataset(path):
    all_files = glob.glob(path + "/*.parquet")

    print(all_files)

    files = []

    for filename in all_files:
        df = pd.read_parquet(filename, engine='pyarrow')
        files.append(df)

    df = pd.concat(files, axis=0, ignore_index=True)
    return df

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
        # https://developer.twitter.com/en/docs/tweets/filter-realtime/api-reference/post-statuses-filter
        # https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
        twitter_stream.filter(track=NATURE_KEYWORDS + SPACE_KEYWORDS + ML_KEYWORDS)

    def get_spark(self):
        # get spark session
        spark = SparkSession.builder. \
            appName("TwitterRawDataIngestion"). \
            master(self._spark_master). \
            config("spark.sql.streaming.checkpointLocation", self._checkpoint_dir). \
            config("spark.sql.warehouse.dir", self._warehouse_location). \
            enableHiveSupport(). \
            getOrCreate()
        return spark

    def get_tweets_df(self):
        spark = self.get_spark()

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

        return tweet_df

    def structured_streaming(self):

        # extract the data as per our schema
        tweet_df = self.get_tweets_df()


        #tweet_df.createGlobalTempView("raw_tweet_df")

        # dump the data into bronze lake path
        storeDF = tweet_df.writeStream. \
            format("parquet"). \
            outputMode("append"). \
            option("path", self._bronze_parquet_dir). \
            option("checkpointLocation", self._checkpoint_dir). \
            trigger(processingTime='10 seconds'). \
            start()

        self.get_spark().streams.awaitAnyTermination()

    def visualize(self):

        tweet_df = self.get_tweets_df()

        def foreach_batch_function(df, epoch_id):
            # Transform and write batchDF
            df.show(50, False)

        tweet_df.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()

    def file_dump(self, path, seconds):
        spark = self.get_spark()

        tweet_df = self.get_tweets_df()

        # dump the data into bronze lake path
        storeDF = tweet_df.writeStream. \
            format(format). \
            outputMode("append"). \
            option("path", path). \
            option("checkpointLocation", self._checkpoint_dir). \
            trigger(processingTime='10 seconds'). \
            start()

        self.get_spark().streams.awaitTerminationOrTimeout(seconds)

        df = get_raw_dataset(path.replace("file://", ""))
        df.to_parquet("data/ssp_dataset.parquet", engine="pyarrow")

if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config.ini",
                          required=False,
                          help="File path of config.ini")

    optparse.add_argument("-m", "--mode",
                          required=True,
                          help="[start_tweet_stream, structured_streaming_dump, visualize, file_dump]")

    optparse.add_argument("-s", "--seconds",
                          required=False,
                          help="Wait seconds before shutting down")

    optparse.add_argument("-p", "--path",
                          required=False,
                          default="file:///tmp/ssp/raw_data/",
                          help="Path to store the records")

    parsed_args = optparse.parse_args()

    dataset = TwitterDataset(config_file_path=parsed_args.config_file)

    if parsed_args.mode == "start_tweet_stream":
        dataset.twitter_socket_stream()
    elif parsed_args.mode == "structured_streaming_dump":
        dataset.structured_streaming()
    elif parsed_args.mode == "visualize":
        dataset.visualize()
    elif parsed_args.mode == "file_dump":
        dataset.file_dump(parsed_args.path, parsed_args.seconds)
    else:
        raise RuntimeError("Invalid choice")
