#!/usr/bin/env python

"""
SSP modules that handles all data at ingestion level from Twitter stream
"""

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import os
import shutil
import gin
import time

import pandas as pd
import glob
from tqdm import tqdm
import psycopg2
# import socket
import threading

from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType
from ssp.logger.pretty_print import print_info

from ssp.utils.ai_key_words import AIKeyWords
from ssp.spark.streaming.common.twitter_streamer_base import TwitterStreamerBase

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



def filter_possible_ai_tweet(text):
    text = text.replace("#", "").replace("@", "")
    for tag in AIKeyWords.POSITIVE.split("|"):
        if f' {tag.lower()} ' in f' {text.lower()} ':
            return 1
    return 0


filter_possible_ai_tweet_udf = udf(filter_possible_ai_tweet, IntegerType())


@gin.configurable
class TwitterDataset(TwitterStreamerBase):
    """
    Twitter ingestion class \n
    - Starts the Spark Structured Streaming against the Kafka topic and dumps the data to HDFS / Postgresql

    :param kafka_bootstrap_servers: (str) Kafka bootstram server
    :param kafka_topic: (str) Kafka topic
    :param checkpoint_dir: (str) Checkpoint directory for fault tolerance
    :param bronze_parquet_dir: (str) Store path to dump tweet data
    :param warehouse_location: Spark warehouse location
    :param spark_master: Spark Master URL
    :param postgresql_host: Postgresql host
    :param postgresql_port: Postgresql port
    :param postgresql_database: Postgresql Database
    :param postgresql_user: Postgresql user name
    :param postgresql_password: Postgresql user password
    :param raw_tweet_table_name_prefix: Postgresql table name prefix
    :param processing_time: Processing time trigger
    """
    def __init__(self,
                 kafka_bootstrap_servers="localhost:9092",
                 kafka_topic="mix_tweets_topic",
                 checkpoint_dir="hdfs://localhost:9000/tmp/ssp/data/lake/checkpoint/",
                 bronze_parquet_dir="hdfs://localhost:9000/tmp/ssp/data/lake/bronze/",
                 warehouse_location="/opt/spark-warehouse/",
                 spark_master="spark://IMCHLT276:7077",
                 postgresql_host="localhost",
                 postgresql_port="5432",
                 postgresql_database="sparkstreamingdb",
                 postgresql_user="sparkstreaming",
                 postgresql_password="sparkstreaming",
                 raw_tweet_table_name_prefix="raw_tweet_dataset",
                 processing_time='5 seconds'):
        TwitterStreamerBase.__init__(self,
                                     spark_master=spark_master,
                                     checkpoint_dir=checkpoint_dir,
                                     warehouse_location=warehouse_location,
                                     kafka_bootstrap_servers=kafka_bootstrap_servers,
                                     kafka_topic=kafka_topic,
                                     processing_time=processing_time)
        self._spark_master = spark_master

        self._kafka_bootstrap_servers = kafka_bootstrap_servers
        self._checkpoint_dir = checkpoint_dir
        self._bronze_parquet_dir = bronze_parquet_dir
        self._warehouse_location = warehouse_location

        self._postgresql_host = postgresql_host
        self._postgresql_port = postgresql_port
        self._postgresql_database = postgresql_database
        self._postgresql_user = postgresql_user
        self._postgresql_password = postgresql_password
        self._broad_cast_raw_tweet_count = self._get_spark().sparkContext.accumulator(0)

        self._kafka_topic = kafka_topic
        self._kafka_ai_topic = "ai_tweets_topic"

        self._raw_tweet_table_name_prefix = raw_tweet_table_name_prefix

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
            # query_to_df the INSERT statement
            cur.query_to_df(get_create_table_sql(table_name=table_name))
            conn.commit()
            cur.close()
        except:
            print_info("Postgresql Error!")

    def check_n_stop_streaming(self, topic, query, num_records, raw_tweet_table_name):
        while (True):
            conn = self.get_postgresql_connection()
            try:
                count = pd.read_sql(f"select count(*) from {raw_tweet_table_name}", conn)["count"][0]
            except Exception as e:
                count = 0

            try:
                print_info(query.lastProgress())
            except:
                pass #print_info("No stream progress")

            if count > num_records:
                print_info(f"Number of records received so far in topic {topic} is {count}")
                query.stop()
                break
            else:
                print_info(f"Number of records received so far in topic {topic} is {count}")
            time.sleep(1)

    def _dump_into_postgresql_internal(self, run_id, kafka_topic, num_records=25000):
        """
        Dumps the live tweet stream into Postgresql DB
        :param run_id:
        :param kafka_topic:
        :param num_records:
        :return:
        """

        tweet_stream = self._get_source_stream(kafka_topic)
        raw_tweet_table_name = self._raw_tweet_table_name_prefix + "_{}".format(run_id)


        def postgresql_all_tweets_data_dump(df,
                                            epoch_id,
                                            raw_tweet_table_name):

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


        query = tweet_stream.writeStream.outputMode("append"). \
            foreachBatch(lambda df, id :
                         postgresql_all_tweets_data_dump(df=df,
                                                         epoch_id=id,
                                                         raw_tweet_table_name=raw_tweet_table_name)).\
            trigger(processingTime=self._processing_time). \
            start()


        monitor_thread = threading.Thread(target=self.check_n_stop_streaming, args=(kafka_topic, query, num_records, raw_tweet_table_name, ))
        monitor_thread.setDaemon(True)
        monitor_thread.start()

        query.awaitTermination()
        monitor_thread.join()

    def dump_into_postgresql(self, run_id, num_records=50000):
        self._dump_into_postgresql_internal(run_id=run_id, kafka_topic=self._kafka_topic, num_records=num_records // 2)
        self._dump_into_postgresql_internal(run_id=run_id, kafka_topic=self._kafka_ai_topic, num_records=num_records)
