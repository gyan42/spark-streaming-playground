import gin
import argparse
import os
import pandas as pd
import numpy as np
import psycopg2
import sqlalchemy

from ssp.logger.pretty_print import print_error, print_info
from ssp.utils.misc import check_n_mk_dirs
from ssp.ml.transformer.ssp_labeller import SSPTextLabeler
from sklearn.model_selection import train_test_split


class PostgresqlDatasetBase(object):
    def __init__(self,
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

    def to_posgresql(self, df, table_name):
        conn = self.get_sqlalchemy_connection()
        try:
            df.to_sql(name=table_name,
                      con=conn,
                      if_exists="fail",
                      index=False)
        except ValueError as e:
            print_error(e)

    def get_latest_dataset(self):
        conn = self.get_sqlalchemy_connection()
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' AND table_type='BASE TABLE'
        """

        tables = sorted(
            [table for table in pd.read_sql(query, conn)["table_name"].values if self._raw_tweet_table_name_prefix in table],
            reverse=True)
        if len(tables) == 0:
            raise UserWarning("No data found in Postgresql DB")

        table_name = tables[0]
        version = table_name.split("_")[-1]
        return table_name, version