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
from ssp.ml.transformer.ssp_labeller import SSPTextLabeler
from sklearn.model_selection import train_test_split

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

        self._labeler = SSPTextLabeler(input_col="text", output_col=label_output_column)

    def prepare(self):
        conn = self.get_sqlalchemy_connection()
        raw_tweet_dataset_table_name, index = self.get_latest_dataset()

        check_n_mk_dirs(f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}")

        # Download dataset as parquet files
        raw_tweet_dataset_df = pd.read_sql(f"select * from {raw_tweet_dataset_table_name}", conn)

        raw_tweet_dataset_df_deduplicated = raw_tweet_dataset_df.drop_duplicates("text")

        raw_tweet_dataset_df_deduplicated = self._labeler.transform(raw_tweet_dataset_df_deduplicated)

        print_info("Record counts per label : ")
        print_info(raw_tweet_dataset_df_deduplicated[self._label_output_column].value_counts())

        # Store the deduplicated tweets collected with respective to AI keywords
        self.to_posgresql(df=raw_tweet_dataset_df_deduplicated,
                          table_name=f"tweet_classification_base_dataset_version_{index}")

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # Stratified sampling and get respective data split. Stoer them as parquet and as well as Posgres table
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        df, test_df = train_test_split(raw_tweet_dataset_df_deduplicated,
                                       test_size=1000,
                                       random_state=42,
                                       stratify=raw_tweet_dataset_df_deduplicated[self._label_output_column])

        self.store_df_as_parquet(df=test_df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/test.parquet")
        self.to_posgresql(df=test_df,
                          table_name=f"test_dataset_version_{index}")

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        df, dev_df = train_test_split(df,
                                      test_size=500,
                                      random_state=42,
                                      stratify=df[self._label_output_column])
        self.store_df_as_parquet(df=dev_df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/dev.parquet")
        self.to_posgresql(df=dev_df,
                          table_name=f"dev_dataset_version_{index}")

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        df, snorkel_train_df = train_test_split(df,
                                                test_size=10000,
                                                random_state=42,
                                                stratify=df[self._label_output_column])
        self.store_df_as_parquet(df=snorkel_train_df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/snorkel_train_df.parquet")
        self.to_posgresql(df=snorkel_train_df,
                          table_name=f"snorkel_train_dataset_version_{index}")

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self.store_df_as_parquet(df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/train.parquet")
        self.to_posgresql(df=df,
                          table_name=f"train_dataset_version_{index}")


if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config.ini",
                          required=False,
                          help="File path of config.ini")

    parsed_args = optparse.parse_args()

    dataset = SSPMLDataset()
    dataset.prepare()
