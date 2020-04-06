import gin
import argparse
import os
import pandas as pd
import numpy as np
import psycopg2
import sqlalchemy

from sklearn.model_selection import train_test_split
from ssp.logger.pretty_print import print_error, print_info
from ssp.ml.transformer.ssp_labeller import SSPTextLabeler


class PostgresqlDatasetBase(object):
    def __init__(self,
                 text_column="text",
                 label_output_column="naive_label",
                 raw_tweet_table_name_prefix="raw_tweet_dataset",
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

        self._raw_tweet_table_name_prefix = raw_tweet_table_name_prefix

        self._label_output_column = label_output_column
        self._text_column = text_column

        self._labeler = SSPTextLabeler(input_col="text", output_col=label_output_column)


    def get_sqlalchemy_connection(self):
        url = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(self._postgresql_user,
                                                            self._postgresql_password,
                                                            self._postgresql_host,
                                                            self._postgresql_port,
                                                            self._postgresql_database)
        # Connect to database (Note: The package psychopg2 is required for Postgres to work with SQLAlchemy)
        engine = sqlalchemy.create_engine(url)
        con = engine.connect()
        return con

    def store_df_as_parquet(self, df, path):
        print_info(f"{df.shape[0]} records will be written to {path}")
        if os.path.exists(path):
            print_error(f"File path {path} exists!\n")
            return
        os.makedirs("/".join(path.split("/")[:-1]), exist_ok=True)
        df["id"] = np.arange(0, len(df), dtype=int)
        df.to_parquet(path, engine="fastparquet", index=False)

    def to_posgresql_table(self, df, table_name, if_exists="fail"):
        conn = self.get_sqlalchemy_connection()
        try:
            df.to_sql(name=table_name,
                      con=conn,
                      if_exists=if_exists,
                      index=False)
        except ValueError as e:
            print_error(e)

    def get_tables_list(self):
        conn = self.get_sqlalchemy_connection()

        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' AND table_type='BASE TABLE'
        """
        return pd.read_sql(query, conn)["table_name"].values

    def get_raw_dump_tables_list(self):
        tables = self.get_tables_list()
        tables = sorted(
            [table for table in tables if table.startswith(self._raw_tweet_table_name_prefix)],
            reverse=True)

        print_info("List of raw dataset tables avaialable : {}\n\n".format("\n".join(tables)))
        if len(tables) == 0:
            raise UserWarning("No data found in Postgresql DB")
        return tables

    def get_latest_raw_dataset_name_n_version(self):
        tables = self.get_raw_dump_tables_list()
        table_name = tables[0]
        version = table_name.split("_")[-1]
        return table_name, version

    def get_table(self, table_name):
        conn = self.get_sqlalchemy_connection()
        return pd.read_sql(f"select * from {table_name}", conn)

    def store_table(self, df, table_name):
        pass

    def get_processed_datasets(self):
        conn = self.get_sqlalchemy_connection()

        raw_tweet_dataset_table_name, index = self.get_latest_raw_dataset_name_n_version()
        tables = self.get_tables_list()
        print_error(tables)

        res = list()

        for table in [f"deduplicated_raw_tweet_dataset_{index}",
                      f"test_dataset_{index}",
                      f"dev_dataset_{index}",
                      f"snorkel_train_dataset_{index}",
                      f"train_dataset_{index}"]:
            print_info(f"Checking for {table}...")

            if table in tables:
                print_info(f"Found {table}!")
                res.append(pd.read_sql(f"select * from {table}", conn))

        raw_tweet_dataset_df_deduplicated, test_df, dev_df, snorkel_train_df, train_df = res
        return raw_tweet_dataset_df_deduplicated, test_df, dev_df, snorkel_train_df, train_df

    def prepare_dataset(self):
        conn = self.get_sqlalchemy_connection()
        raw_tweet_dataset_table_name, index = self.get_latest_raw_dataset_name_n_version()

        # Download dataset from postgresql
        raw_tweet_dataset_df = pd.read_sql(f"select * from {raw_tweet_dataset_table_name}", conn)

        raw_tweet_dataset_df_deduplicated = raw_tweet_dataset_df.drop_duplicates("text")

        raw_tweet_dataset_df_deduplicated = self._labeler.transform(raw_tweet_dataset_df_deduplicated)

        print_info("Record counts per label : ")
        print_info(raw_tweet_dataset_df_deduplicated[self._label_output_column].value_counts())

        df, test_df = train_test_split(raw_tweet_dataset_df_deduplicated,
                                       test_size=1000,
                                       random_state=42,
                                       stratify=raw_tweet_dataset_df_deduplicated[self._label_output_column])

        df, dev_df = train_test_split(df,
                                      test_size=500,
                                      random_state=42,
                                      stratify=df[self._label_output_column])

        train_df, snorkel_train_df = train_test_split(df,
                                                      test_size=10000,
                                                      random_state=42,
                                                      stratify=df[self._label_output_column])

        return raw_tweet_dataset_df_deduplicated, test_df, dev_df, snorkel_train_df, train_df