#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

from ssp.utils.config_manager import ConfigManager

class StreamingConfigs(object):
    """
    Reads the config.ini using configparser
    """
    def __init__(self, config_file_path, twitter_ini_file="twitter.ini"):

        self._config = ConfigManager(config_path=config_file_path)

        if twitter_ini_file:
            self._twitter_config = ConfigManager(config_path=twitter_ini_file)


        # [spark]
        self._spark_master = self._config.get_item("spark", "master")
        self._kafka_bootstrap_servers = self._config.get_item("spark", "kafka_bootstrap_servers")
        self._kafka_topic = self._config.get_item("spark", "kafka_topic")
        self._warehouse_location = self._config.get_item("spark", "warehouse_location")
        self._processing_time = self._config.get_item("spark", "processing_time")

        # [twitter]
        if twitter_ini_file:
            self._twitter_consumer_key = self._twitter_config.get_item("twitter", "consumer_key")
            self._twitter_consumer_secret = self._twitter_config.get_item("twitter", "consumer_secret")
            self._twitter_access_token = self._twitter_config.get_item("twitter", "access_token")
            self._twitter_access_secret = self._twitter_config.get_item("twitter", "access_secret")

        # [dataset]
        self._checkpoint_dir = self._config.get_item("dataset", "checkpoint_dir")
        self._remove_old_data = self._config.get_item_as_boolean("dataset", "remove_old_data")
        self._bronze_parquet_dir = self._config.get_item("dataset", "bronze_parquet_dir")
        self._silver_parquet_dir = self._config.get_item("dataset", "silver_parquet_dir")
        self._gold_parquet_dir = self._config.get_item("dataset", "gold_parquet_dir")
        self._bronze_hive_manifest_location = self._config.get_item("dataset", "bronze_hive_manifest_location")
        self._silver_hive_manifest_location = self._config.get_item("dataset", "silver_hive_manifest_location")
        self._gold_hive_manifest_location = self._config.get_item("dataset", "gold_hive_manifest_location")
        self._raw_tweet_table_name = self._config.get_item("dataset", "raw_tweet_table_name")
        self._ai_tweet_table_name = self._config.get_item("dataset", "ai_tweet_table_name")

        # [kafka]
        self._kafka_addr = self._config.get_item("kafka", "kafka_addr")
        self._kafka_topic = self._config.get_item("kafka", "topic")

        # [postgresql]
        self._postgresql_host = self._config.get_item("postgresql", "host")
        self._postgresql_port = self._config.get_item("postgresql", "port")
        self._postgresql_database = self._config.get_item("postgresql", "database")
        self._postgresql_user = self._config.get_item("postgresql", "user")
        self._postgresql_password = self._config.get_item("postgresql", "password")
