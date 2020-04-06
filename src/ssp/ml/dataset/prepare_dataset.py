import gin
import argparse
import os
import pandas as pd
import numpy as np
import psycopg2
import sqlalchemy

from ssp.posgress.dataset_base import PostgresqlDatasetBase
from ssp.utils.misc import check_n_mk_dirs
from ssp.logger.pretty_print import print_info, print_error

@gin.configurable
class SSPMLDataset(PostgresqlDatasetBase):
    def __init__(self,
                 label_output_column="naive_label",
                 raw_tweet_table_name_prefix="raw_tweet_dataset",
                 postgresql_host="localhost",
                 postgresql_port="5432",
                 postgresql_database="sparkstreamingdb",
                 postgresql_user="sparkstreaming",
                 postgresql_password="sparkstreaming"):

        PostgresqlDatasetBase.__init__(self,
                                       label_output_column=label_output_column,
                                       raw_tweet_table_name_prefix=raw_tweet_table_name_prefix,
                                       postgresql_host=postgresql_host,
                                       postgresql_port=postgresql_port,
                                       postgresql_database=postgresql_database,
                                       postgresql_user=postgresql_user,
                                       postgresql_password=postgresql_password)

    def store(self):
        raw_tweet_dataset_df_deduplicated, test_df, dev_df, snorkel_train_df, train_df = self.prepare_dataset()

        raw_tweet_dataset_table_name, index = self.get_latest_raw_dataset_name_n_version()

        check_n_mk_dirs(f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}")

        # Store the deduplicated tweets collected with respective to AI keywords
        self.to_posgresql_table(df=raw_tweet_dataset_df_deduplicated,
                                table_name=f"deduplicated_raw_tweet_dataset_{index}")
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=test_df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/test.parquet")
        self.to_posgresql_table(df=test_df,
                                table_name=f"test_dataset_{index}")
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=dev_df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/dev.parquet")
        self.to_posgresql_table(df=dev_df,
                                table_name=f"dev_dataset_{index}")
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=snorkel_train_df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/snorkel_train_df.parquet")
        self.to_posgresql_table(df=snorkel_train_df,
                                table_name=f"snorkel_train_dataset_{index}")

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self.store_df_as_parquet(train_df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/train.parquet")
        self.to_posgresql_table(df=train_df,
                                table_name=f"train_dataset_{index}")


if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config.ini",
                          required=False,
                          help="File path of config.ini")

    parsed_args = optparse.parse_args()

    dataset = SSPMLDataset()
    dataset.store()
