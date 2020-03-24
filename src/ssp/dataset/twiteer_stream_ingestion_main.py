#!/usr/bin/env python

"""
SSP modules that handles all data at ingestion level frm Twitter stream
"""

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import argparse
import os
import shutil
from threading import Thread, Event
from tweepy.auth import OAuthHandler
from tweepy.streaming import Stream, StreamListener
from tweepy.streaming import StreamListener

import pandas as pd
import glob
import numpy as np
from tqdm import tqdm

# import socket
from kafka import KafkaProducer
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, regexp_replace
from pyspark.sql.types import StructType, StringType, IntegerType, ArrayType
from pyspark.sql.functions import col, isnull
from ssp.utils.config_manager import ConfigManager, print_info
from ssp.utils.configuration import StreamingConfigs

# Twitter Filter Tags

AI_KEYWORDS = []


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
    """
    Combines all parquet file as one in given path
    :param path: Folder path
    :return:
    """
    all_files = glob.glob(path + "/*.parquet")
    files = []
    for filename in tqdm(all_files):
        df = pd.read_parquet(filename, engine="fastparquet")
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

    def twitter_kafka_stream(self):
        auth = OAuthHandler(self._twitter_consumer_key, self._twitter_consumer_secret)
        auth.set_access_token(self._twitter_access_token, self._twitter_access_secret)

        twitter_stream = Stream(auth, TweetsListener(kafka_addr=self._kafka_addr, topic=self._kafka_topic))
        # https://developer.twitter.com/en/docs/tweets/filter-realtime/api-reference/post-statuses-filter
        # https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
        twitter_stream.filter(track=self._key_words, languages=["en"])

    def get_spark(self):
        """
        :return:Spark Session
        """
        spark = SparkSession.builder. \
            appName("TwitterRawDataIngestion"). \
            master(self._spark_master). \
            config("spark.sql.streaming.checkpointLocation", self._checkpoint_dir). \
            config("spark.sql.warehouse.dir", self._warehouse_location). \
            enableHiveSupport(). \
            getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")

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

        # define the schema to extract the data we are interested
        # https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object
        urls = ArrayType(StructType().\
        add("expanded_url", StringType(), True))

        media = ArrayType(StructType().\
        add("media_url", StringType(), True). \
        add("media_url_https", StringType(), True))

        # Tweet -> Entities{} -> Urls[] -> Media[]
        entities = StructType(). \
            add("urls", urls, True). \
            add("media", media)

        schema = StructType(). \
            add('created_at', StringType(), False). \
            add('source', StringType(), False). \
            add('text', StringType(), False). \
            add('extended_tweet', StructType().add("full_text", StringType(), True), True). \
            add('entities', entities, False). \
            add('retweeted_status', StructType().add('user', StructType().add('description', StringType())), True). \
            add('geo', StringType(), True). \
            add('retweet_count', IntegerType(), True)

        # extract the data as per our schema
        tweet_df = tweet_stream. \
            selectExpr("cast (value as STRING)"). \
            select(from_json("value", schema).
                   alias("temp")). \
            select(["temp.created_at",
                    "temp.text",
                    "temp.source",
                    "temp.extended_tweet.full_text",
                    "temp.entities.urls.expanded_url",
                    "temp.entities.media.media_url_https"]). \
            withColumn("source", regexp_replace("source", "<[^>]*>", "")). \
            where(~isnull(col("full_text")))

        return tweet_df

    def structured_streaming_dump(self):
        """
        Reads the data from Kafka topic and dumps the data into Bronze lake (HDFS path to store RAW data)
        :return:
        """

        # extract the data as per our schema
        tweet_df = self.get_tweets_df()

        #tweet_df.createGlobalTempView("raw_tweet_df")

        # dump the data into bronze lake path
        storeDF = tweet_df.writeStream. \
            format("parquet"). \
            outputMode("append"). \
            option("path", self._bronze_parquet_dir). \
            option("checkpointLocation", self._checkpoint_dir). \
            trigger(processingTime=self._processing_time). \
            start()

        self.get_spark().streams.awaitAnyTermination()

    def visualize(self):
        """
        For debugging purporse
        :return:
        """

        tweet_df = self.get_tweets_df()

        def foreach_batch_function(df, epoch_id):
            # Transform and write batchDF
            df.show(50, True)

        tweet_df.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()

    def local_dir_dump(self, path, seconds):
        """
        Reads the data from Kafka topic and dumps the data into local directory
        :param path:
        :param seconds:
        :return:
        """
        spark = self.get_spark()

        tweet_df = self.get_tweets_df()

        # dump the data into bronze lake path
        storeDF = tweet_df.writeStream. \
            format("parquet"). \
            outputMode("append"). \
            option("path", path). \
            option("checkpointLocation", self._checkpoint_dir). \
            trigger(processingTime=self._processing_time). \
            start().awaitTermination(int(seconds))

    def parquet_part_files_to_ssp_dataset(self, path):
        """
        Reads the parquet part files and constructs the dataset fro ML training
        :param path:
        :return:
        """

        if not os.path.exists("data/dataset/ssp/original/"):
            os.makedirs("data/dataset/ssp/original/")

        def store_df_as_parquet(df, path):
            df["id"] = np.arange(0, len(df), dtype=int)
            # df["label"] = df["text"].apply(labelme)
            df = df[["id", "text"]]
            df.to_parquet(path, engine="fastparquet", index=False)


        df = get_raw_dataset(path.replace("file://", ""))

        df.drop_duplicates(["full_text"], inplace=True)
        df["expanded_url"] = df["expanded_url"].astype(str)
        df["media_url_https"] = df["media_url_https"].astype(str)
        df["text"] = df["full_text"]
        df = df.drop(["full_text"], axis=1)

        print_info(df.shape)

        assert df.shape[0] > 27500
        df = df.sample(frac=1).reset_index(drop=True)
        df.to_parquet("data/dataset/ssp/original/ssp_tweet_dataset.parquet", engine="fastparquet", index=False)

        unlabeled_test_df = df[0:1000]  # 1K
        store_df_as_parquet(df=unlabeled_test_df, path="data/dataset/ssp/original/ssp_test_dataset.parquet")

        unlabeled_val_df = df[1000:1500]  # 500
        store_df_as_parquet(df=unlabeled_val_df, path="data/dataset/ssp/original/ssp_val_dataset.parquet")

        unlabeled_LF_df = df[1500:2500]  # 1K
        store_df_as_parquet(df=unlabeled_LF_df, path="data/dataset/ssp/original/ssp_LF_dataset.parquet")

        unlabeled_train_df = df[2500:]  # 25+K
        unlabeled_train_df.to_parquet("data/dataset/ssp/original/ssp_train_dataset.parquet", engine="fastparquet", index=False)


if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config.ini",
                          required=False,
                          help="File path of config.ini")

    optparse.add_argument("-m", "--mode",
                          required=True,
                          help="[start_tweet_stream, structured_streaming_dump, visualize, local_dir_dump, ssp_dataset]")

    optparse.add_argument("-s", "--seconds",
                          required=False,
                          type=int,
                          help="Wait seconds before shutting down")

    optparse.add_argument("-p", "--path",
                          required=False,
                          default="file:///tmp/ssp/raw_data/",
                          help="Path to store the records")

    parsed_args = optparse.parse_args()

    dataset = TwitterDataset(config_file_path=parsed_args.config_file)

    if parsed_args.mode == "start_tweet_stream":
        dataset.twitter_kafka_stream()
    elif parsed_args.mode == "structured_streaming_dump":
        dataset.structured_streaming_dump()
    elif parsed_args.mode == "visualize":
        dataset.visualize()
    elif parsed_args.mode == "local_dir_dump":
        dataset.local_dir_dump(parsed_args.path, parsed_args.seconds)
    elif parsed_args.mode == "ssp_dataset":
        dataset.parquet_part_files_to_ssp_dataset(path=parsed_args.path)
    else:
        raise RuntimeError("Invalid choice")
