#!/usr/bin/env python

"""
SSP modules that handles all data at ingestion level frm Twitter stream
"""
from ssp.ml.transformer.ssp_labeller import labelme_udf
from ssp.ml.transformer.text_preprocessor import preprocess_udf

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
import re
import shutil

import pandas as pd
import glob
import numpy as np
from tqdm import tqdm
import psycopg2
# import socket

from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StringType, IntegerType, ArrayType, BooleanType
from pyspark.sql.functions import col, isnull
from pyspark.sql.functions import sha2, concat_ws

from ssp.utils.config_manager import ConfigManager, print_info
from ssp.utils.configuration import StreamingConfigs
from ssp.kafka.consumer.streamer_base import StreamerBase
from ssp.snorkel.ai_key_words import AIKeyWords

# Twitter Filter Tags


def get_create_table_sql(table_name):
    sql_str = """
    CREATE TABLE  IF NOT EXISTS {} (
       id_str VARCHAR (100) NOT NULL,
       created_at VARCHAR (100) NOT NULL,
       source VARCHAR (50) NOT NULL,
       text VARCHAR (2048) NOT NULL,
       expanded_url VARCHAR (1024),
       media_url_https VARCHAR (1024),
       hash VARCHAR (512));
    """.format(table_name)
    return sql_str

def check_table_exists(table_name, schema="public"):
    sql_str = """
        SELECT to_regclass('{}.{}') as table;
    """.format(schema, table_name)
    return sql_str

def check_n_mk_dirs(path, is_remove=False):
    if os.path.exists(path):
        if is_remove:
            shutil.rmtree(path)
    else:
        os.makedirs(path)


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


def filter_possible_ai_tweet(text):
    text = text.replace("#", "").replace("@", "")
    for tag in AIKeyWords.ALL.split("|"):
        if f' {tag.lower()} ' in f' {text.lower()} ':
            return 1
    return 0


filter_possible_ai_tweet_udf = udf(filter_possible_ai_tweet, IntegerType())


class TwitterDataset(StreamingConfigs, StreamerBase):
    """
    Twitter ingestion class
    - Gets the twitter stream data and dumps the data into Kafka topic
    - Starts the Spark Structured Streaming against the Kafka topic and dumps the data to HDFS
    """
    def __init__(self, config_file_path):
        StreamingConfigs.__init__(self, config_file_path=config_file_path)
        self._config = ConfigManager(config_path=config_file_path)

        self._broad_cast_raw_tweet_count = self.get_spark().sparkContext.accumulator(0)

    def get_schema(self):
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
            select(from_json("value", self.get_schema()).
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

    def dump_into_bronze_lake(self):
        self.structured_streaming_dump(path=self._bronze_parquet_dir)

    def get_postgresql_connection(self):
        return psycopg2.connect(host=self._postgresql_host,
                                port=self._postgresql_port,
                                database=self._postgresql_database,
                                user=self._postgresql_user,
                                password=self._postgresql_password)

    def check_n_define_table_schema(self, table_name):
        conn = self.get_postgresql_connection()
        # Load the data
        try:
            cur = conn.cursor()
            # execute the INSERT statement
            cur.execute(get_create_table_sql(table_name=table_name))
            conn.commit()
            cur.close()
        except:
            print_info("Postgresql Error!")

    def dump_into_postgresql(self, run_id, seconds):

        tweet_stream = self.get_source_stream()
        raw_tweet_table_name = self._raw_tweet_table_name + "version_{}".format(run_id)

        def postgresql_all_tweets_data_dump(df, epoch_id, raw_tweet_table_name, ai_tweet_table_name):

            # DROP TABLE IF EXISTS ssp_raw_tweet_dataset_0 CASCADE;
            # Transform and write batchDF

            print_info("Raw  Tweets...")
            df.select(["text"]).show(50, False)

            mode = "append"
            url = "jdbc:postgresql://{}:{}/{}".format(self._postgresql_host,
                                                      self._postgresql_port,
                                                      self._postgresql_database)
            properties = {"user": self._postgresql_user,
                          "password": self._postgresql_password,
                          "driver": "org.postgresql.Driver"}
            df.write.jdbc(url=url, table=raw_tweet_table_name, mode=mode, properties=properties)


        tweet_stream.writeStream.outputMode("append"). \
            foreachBatch(lambda df, id :
                         postgresql_all_tweets_data_dump(df=df,
                                                         epoch_id=id,
                                                         raw_tweet_table_name=raw_tweet_table_name,
                                                         ai_tweet_table_name=ai_tweet_table_name)).start().awaitTermination(seconds)


if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config.ini",
                          required=False,
                          help="File path of config.ini")

    optparse.add_argument("-m", "--mode",
                          required=True,
                          help="[dump_into_bronze_lake, visualize, local_dir_dump, dump_into_postgresql]")

    optparse.add_argument("-s", "--seconds",
                          required=False,
                          type=int,
                          help="Wait seconds before shutting down")

    optparse.add_argument("-id", "--run_id",
                          required=False,
                          type=int,
                          help="Run ID")

    optparse.add_argument("-p", "--path",
                          required=False,
                          default="file:///tmp/ssp/raw_data/",
                          help="Path to store the records")

    parsed_args = optparse.parse_args()

    dataset = TwitterDataset(config_file_path=parsed_args.config_file)

    if parsed_args.mode == "dump_into_bronze_lake":
        dataset.dump_into_bronze_lake()
    elif parsed_args.mode == "visualize":
        dataset.visualize()
    elif parsed_args.mode == "local_dir_dump":
        dataset.structured_streaming_dump(path=parsed_args.path, termination_time=int(parsed_args.seconds))
    elif parsed_args.mode == "dump_into_postgresql":
        dataset.dump_into_postgresql(run_id=parsed_args.run_id, seconds=parsed_args.seconds)
    else:
        raise RuntimeError("Invalid choice")
