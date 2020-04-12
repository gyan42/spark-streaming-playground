import gin
import argparse
import os
import pandas as pd
import numpy as np
import psycopg2
import sqlalchemy

from ssp.ml.transformer import SSPTextLabeler
from ssp.posgress.dataset_base import PostgresqlDatasetBase
from ssp.snorkel.labelling_function import SSPTweetLabeller
from ssp.utils.misc import check_n_mk_dirs
from ssp.logger.pretty_print import print_info, print_error

@gin.configurable
class SSPMLDataset(PostgresqlDatasetBase):
    def __init__(self,
                 text_column="text",
                 label_output_column="slabel",
                 raw_tweet_table_name_prefix="raw_tweet_dataset",
                 postgresql_host="localhost",
                 postgresql_port="5432",
                 postgresql_database="sparkstreamingdb",
                 postgresql_user="sparkstreaming",
                 postgresql_password="sparkstreaming",
                 overwrite=False):

        PostgresqlDatasetBase.__init__(self,
                                       text_column=text_column,
                                       label_output_column=label_output_column,
                                       raw_tweet_table_name_prefix=raw_tweet_table_name_prefix,
                                       postgresql_host=postgresql_host,
                                       postgresql_port=postgresql_port,
                                       postgresql_database=postgresql_database,
                                       postgresql_user=postgresql_user,
                                       postgresql_password=postgresql_password)
        self._overwrite = overwrite
        self._labeler = SSPTweetLabeller(input_col="text", output_col=label_output_column)

    def store(self, version=0):
        raw_tweet_dataset_df_deduplicated, test_df, dev_df, snorkel_train_df, train_df = self.split_dataset_table(version=version)

        self._labeler = self._labeler.fit(snorkel_train_df)
        test_df = self._labeler.transform(test_df)
        dev_df = self._labeler.transform(dev_df)
        train_df = self._labeler.transform(train_df)


        raw_tweet_dataset_table_name = self.get_latest_raw_dataset_name_n_version(version=version)

        check_n_mk_dirs(f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}")

        if self._overwrite:
            if_exists = "replace"
        else:
            if_exists = "fail"

        # Store the deduplicated tweets collected with respective to AI keywords
        self.to_posgresql_table(df=raw_tweet_dataset_df_deduplicated,
                                table_name=f"deduplicated_{raw_tweet_dataset_table_name}",
                                if_exists=if_exists)
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=test_df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/test.parquet")
        self.to_posgresql_table(df=test_df,
                                table_name=f"test_dataset_{version}",
                                if_exists=if_exists)
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=dev_df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/dev.parquet")
        self.to_posgresql_table(df=dev_df,
                                table_name=f"dev_dataset_{version}",
                                if_exists=if_exists)
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=snorkel_train_df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/snorkel_train_df.parquet")
        self.to_posgresql_table(df=snorkel_train_df,
                                table_name=f"snorkel_train_dataset_{version}",
                                if_exists=if_exists)

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self.store_df_as_parquet(train_df,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/train.parquet")
        self.to_posgresql_table(df=train_df,
                                table_name=f"train_dataset_{version}",
                                if_exists=if_exists)
