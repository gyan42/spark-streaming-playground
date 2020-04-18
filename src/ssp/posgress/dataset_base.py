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
import argparse
import os
import pandas as pd
import numpy as np
import psycopg2
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import swifter
from sklearn.model_selection import train_test_split
from ssp.logger.pretty_print import print_error, print_info
from absl import flags
from absl import app

@gin.configurable
class PostgresqlConnection(object):
    """
    Postgresql utility class to read,write tables and execute query

    :param postgresql_host: Postgresql Host address
    :param postgresql_port: Postgresql port number
    :param postgresql_database: Postgresql database name
    :param postgresql_user: Postgresql user name
    :param postgresql_password: Postgresql password
    """
    def __init__(self,
                 postgresql_host="localhost",
                 postgresql_port="5432",
                 postgresql_database="sparkstreamingdb",
                 postgresql_user="sparkstreaming",
                 postgresql_password="sparkstreaming"):

        self._postgresql_host = postgresql_host
        self._postgresql_port = postgresql_port
        self._postgresql_database = postgresql_database
        self._postgresql_user = postgresql_user
        self._postgresql_password = postgresql_password

        self._db_url = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(self._postgresql_user,
                                                                     self._postgresql_password,
                                                                     self._postgresql_host,
                                                                     self._postgresql_port,
                                                                     self._postgresql_database)
        self._sqlalchemy_engine = None
        self._sqlalchemy_session = None
        self._sqlalchemy_connection = None

    def get_sqlalchemy_session(self):
        if self._sqlalchemy_session:
            return self._sqlalchemy_session

        if self._sqlalchemy_engine is None:
            self._sqlalchemy_engine = create_engine(self._db_url, pool_recycle=3600)

        session = sessionmaker(bind=self._sqlalchemy_engine)
        self._sqlalchemy_session = session()
        return self._sqlalchemy_session

    def get_sqlalchemy_connection(self):
        """
        :return: Returns postgresql sqlalchemy connection
        """
        if self._sqlalchemy_connection:
            return self._sqlalchemy_connection

        # Connect to database (Note: The package psychopg2 is required for Postgres to work with SQLAlchemy)
        if self._sqlalchemy_engine is None:
            self._sqlalchemy_engine = create_engine(self._db_url, pool_recycle=3600)

        self._sqlalchemy_connection = self._sqlalchemy_engine.connect()
        return self._sqlalchemy_connection

    def store_df_as_parquet(self, df, path, overwrite=False):
        """
        Stores the DataFrame as parquet
        :param df: Pandas DataFrame
        :param path: Local machine path
        :return: None
        """
        print_info(f"{df.shape[0]} records will be written to {path}")

        if os.path.exists(path):
            print_error(f"File path {path} exists!\n")
            if overwrite:
            	os.remove(path)
            return
        os.makedirs("/".join(path.split("/")[:-1]), exist_ok=True)
        df["id"] = np.arange(0, len(df), dtype=int)
        df.to_parquet(path, engine="fastparquet", index=False)


    def to_posgresql_table(self, df, table_name, schema="public", if_exists="fail"):
        """
        Stores the DataFrame as Postgresql table
        :param df: Pandas Dataframe
        :param table_name: Name of the table
        :param if_exists: {'fail', 'replace', 'append'}, default 'fail'
            How to behave if the table already exists.

            * fail: Raise a ValueError.
            * replace: Drop the table before inserting new values.
            * append: Insert new values to the existing table.
        :return:
        """
        conn = self.get_sqlalchemy_connection()
        try:
            df.to_sql(name=table_name,
                      con=conn,
                      if_exists=if_exists,
                      index=False,
                      schema=schema)
        except ValueError as e:
            print_error(e)

    def get_tables_list(self, table_schema="public"):
        """
        :param table_schema: Postgresql schema. Default is `public`
        :return: List of tables on given table schema
        """
        conn = self.get_sqlalchemy_connection()

        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' AND table_type='BASE TABLE'
        """
        return pd.read_sql(query, conn)["table_name"].values

    def get_table(self, table_name):
        """
        Use to get the Postgresql table as Pandas dataframe
        :param table_name:
        :return: Pandas DataFrame
        """
        conn = self.get_sqlalchemy_connection()
        return pd.read_sql(f"select * from {table_name}", conn)

    def run_query(self, query):
        print_info(f"Runing query : {query}")
        sql = text(query)
        result = self._sqlalchemy_engine.execute(sql)
        return result

    def query_to_df(self, query):
        print_info(f"Runing query : {query}")
        conn = self.get_sqlalchemy_connection()
        return pd.read_sql_query(query, conn)

@gin.configurable
class PostgresqlDatasetBase(PostgresqlConnection):
    def __init__(self,
                 text_column="text",
                 label_output_column="slabel",
                 raw_tweet_table_name_prefix="raw_tweet_dataset",
                 postgresql_host="localhost",
                 postgresql_port="5432",
                 postgresql_database="sparkstreamingdb",
                 postgresql_user="sparkstreaming",
                 postgresql_password="sparkstreaming"):
        """
        Base interface to interact with Dataset tables stored in Postgresql Database
        :param text_column: Name of the text column
        :param label_output_column: Label column to be used while running labeller function
        :param raw_tweet_table_name_prefix: String prefix of the raw table dumpped by Spark streaming prefixed with index
        :param postgresql_host: Postgresql Host address
        :param postgresql_port: Postgresql port number
        :param postgresql_database: Postgresql database name
        :param postgresql_user: Postgresql user name
        :param postgresql_password: Postgresql password
        """
        PostgresqlConnection.__init__(self,
                                      postgresql_host=postgresql_host,
                                      postgresql_port=postgresql_port,
                                      postgresql_database=postgresql_database,
                                      postgresql_user=postgresql_user,
                                      postgresql_password=postgresql_password)
        self._postgresql_host = postgresql_host
        self._postgresql_port = postgresql_port
        self._postgresql_database = postgresql_database
        self._postgresql_user = postgresql_user
        self._postgresql_password = postgresql_password

        self._raw_tweet_table_name_prefix = raw_tweet_table_name_prefix

        self._label_output_column = label_output_column
        self._text_column = text_column

    def get_processed_datasets(self, version=0):
        conn = self.get_sqlalchemy_connection()

        raw_tweet_dataset_table_name = self.get_latest_raw_dataset_name(version=version)
        tables = self.get_tables_list()
        print_error(tables)

        res = list()

        for table in [f"deduplicated_raw_tweet_dataset_{version}",
                      f"test_dataset_{version}",
                      f"dev_dataset_{version}",
                      f"snorkel_train_dataset_{version}",
                      f"train_dataset_{version}"]:
            print_info(f"Checking for {table}...")

            if table in tables:
                print_info(f"Found {table}!")
                res.append(pd.read_sql(f"select * from {table}", conn))
        print_error(len(res))

        raw_tweet_dataset_df_deduplicated, test_df, dev_df, snorkel_train_df, train_df = res
        return raw_tweet_dataset_df_deduplicated, test_df, dev_df, snorkel_train_df, train_df

    def get_raw_dump_tables_list(self):
        """
        Returns list of raw data tables dataset dumped by ~ssp.spark.consumer.TwitterDataset
        :return: List of string Eg: [raw_tweet_dataset_0,raw_tweet_dataset_1]
        """
        tables = self.get_tables_list()
        tables = sorted(
            [table for table in tables if table.startswith(self._raw_tweet_table_name_prefix)],
            reverse=False)

        print_info("List of raw dataset tables avaialable : {}\n\n".format("\n".join(tables)))
        if len(tables) == 0:
            raise UserWarning("No data found in Postgresql DB")
        return tables

    def get_latest_raw_dataset_name(self, version=0):
        """
        Returns the specific version of raw tweet table
        :param version: (int) Run id/version used while dumping the data using ~ssp.spark.consumer.TwitterDataset
        :return: (str) name of the table with version
        """
        tables = self.get_raw_dump_tables_list()
        table_name = tables[version]
        # asserts we have the requested version
        assert version == int(table_name.split("_")[-1])
        return table_name

    def split_dataset_table(self, version=0):
        conn = self.get_sqlalchemy_connection()
        raw_tweet_dataset_table_name = self.get_latest_raw_dataset_name(version=version)

        # Download dataset from postgresql
        raw_tweet_dataset_df = pd.read_sql(f"select * from {raw_tweet_dataset_table_name}", conn)

        # TODO deduplicate here ?
        raw_tweet_dataset_df[self._text_column] = raw_tweet_dataset_df[self._text_column].swifter.apply(lambda t: t.strip())

        raw_tweet_dataset_df_deduplicated = raw_tweet_dataset_df.drop_duplicates(self._text_column)

        raw_tweet_dataset_df_deduplicated = raw_tweet_dataset_df_deduplicated.sample(frac=1, random_state=42).reset_index(drop=True)

        df, test_df = train_test_split(raw_tweet_dataset_df_deduplicated,
                                       test_size=1000,
                                       random_state=42)

        df, dev_df = train_test_split(df,
                                      test_size=500,
                                      random_state=42)

        train_df, snorkel_train_df = train_test_split(df,
                                                      test_size=10000,
                                                      random_state=42)

        return raw_tweet_dataset_df_deduplicated, test_df, dev_df, snorkel_train_df, train_df


flags.DEFINE_string("mode", "download", "[download/upload] tables")
FLAGS = flags.FLAGS


def main(argv):
    db = PostgresqlDatasetBase()
    if FLAGS.mode == "download":
        df = db.get_table("raw_tweet_dataset_0")
        df.to_parquet("data/dataset/ssp/dump/raw_tweet_dataset_0.parquet", engine="fastparquet")
    else:
        df = pd.read_parquet("data/dataset/ssp/dump/raw_tweet_dataset_0.parquet", engine="fastparquet")

        db.to_posgresql_table(df=df, table_name="raw_tweet_dataset_0", if_exists="fail")


if __name__ == "__main__":
    app.run(main)
