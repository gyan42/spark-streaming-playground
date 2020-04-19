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

from ssp.ml.transformer import SSPTextLabeler
from ssp.posgress.dataset_base import PostgresqlDatasetBase
from ssp.snorkel.labelling_function import SSPTweetLabeller
from ssp.utils.misc import check_n_mk_dirs
from ssp.logger.pretty_print import print_info, print_error, print_warn


def insert_id_col(df):
    """
    Inserts `text_id` column considering the number of rows and a label column.
    `label` column copies the values of `slabel` column, if exists or inserts `-1` as value
    :param df: Pandas DataFrame
    :return: Pandas DataFrame
    """
    df["text_id"] = list(range(1, df.shape[0]+1))
    return df


@gin.configurable
class SSPMLDataset(PostgresqlDatasetBase):
    """
    Reads the raw tweet data dump from Postgresql, splits the data and annotates the text with Snorkel. \n
    Dumps the data into postgresql for annotation and conitnuous improvement purpose \n
    Dumps the data into given path as train/dev/test/snorkell train data for model building

    :param text_column: Name of the text column
    :param label_output_column:  Name of the label column to be created using the snorkel labeler
    :param raw_tweet_table_name_prefix: Raw tweet table dump name prefix
    :param postgresql_host: Postgresql host
    :param postgresql_port: Postgresql port
    :param postgresql_database: Postgresql Database
    :param postgresql_user: Postgresql user name
    :param postgresql_password: Postgresql user password
    :param overwrite: Overwrite the table and disk data

    .. code-block:: python

            |Table Name                        |Records|Info                       |
            |----------------------------------|-------|---------------------------|
            |raw_tweet_dataset_0               | 50K+  |Full Raw Dataset           |
            |deduplicated_raw_tweet_dataset_0  | ~     |Depulicated on text column |
            |test_dataset_0                    |1000   |Test dataset               |
            |dev_dataset_0                     |500    |Dev dataset                |
            |snorkel_train_dataset_0           |10K    |Snorkel train dataset      |
            |train_dataset_0                   |~      |Model train dataset        |

    """
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
        self._snorkel_labeler = SSPTweetLabeller(input_col="text", output_col=label_output_column)
        self._naive_labeler = SSPTextLabeler(input_col="text", output_col="label")

    def split_n_store(self, version=0):
        raw_tweet_dataset_table_name = self.get_latest_raw_dataset_name(version=version)

        raw_tweet_dataset_df_deduplicated, test_df, dev_df, snorkel_train_df, train_df = self.split_dataset_table(
                version=version)

        self._snorkel_labeler = self._snorkel_labeler.fit(snorkel_train_df)
        test_df = self._snorkel_labeler.transform(test_df)
        dev_df = self._snorkel_labeler.transform(dev_df)
        train_df = self._snorkel_labeler.transform(train_df)

        test_df = self._naive_labeler.transform(test_df)
        dev_df = self._naive_labeler.transform(dev_df)
        train_df = self._naive_labeler.transform(train_df)

        raw_tweet_dataset_df_deduplicated, \
        test_df, dev_df, snorkel_train_df, train_df = insert_id_col(raw_tweet_dataset_df_deduplicated), \
                                                      insert_id_col(test_df), insert_id_col(dev_df), \
                                                      insert_id_col(snorkel_train_df), \
                                                      insert_id_col(train_df)

        check_n_mk_dirs(f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}")

        if self._overwrite:
            if_exists = "replace"
        else:
            if_exists = "fail"

        # Store the deduplicated tweets collected with respective to AI keywords
        self.to_posgresql_table(df=insert_id_col(raw_tweet_dataset_df_deduplicated),
                                table_name=f"deduplicated_{raw_tweet_dataset_table_name}",
                                if_exists=if_exists)
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=test_df,
                                 overwrite=self._overwrite,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/test.parquet")
        self.to_posgresql_table(df=test_df,
                                table_name=f"test_dataset_{version}",
                                if_exists=if_exists)
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=dev_df,
                                 overwrite=self._overwrite,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/dev.parquet")
        self.to_posgresql_table(df=dev_df,
                                table_name=f"dev_dataset_{version}",
                                if_exists=if_exists)
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=snorkel_train_df,
                                 overwrite=self._overwrite,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/snorkel_train_df.parquet")
        self.to_posgresql_table(df=snorkel_train_df,
                                table_name=f"snorkel_train_dataset_{version}",
                                if_exists=if_exists)

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self.store_df_as_parquet(train_df,
                                 overwrite=self._overwrite,
                                 path=f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}/train.parquet")
        self.to_posgresql_table(df=train_df,
                                table_name=f"train_dataset_{version}",
                                if_exists=if_exists)

    def download_n_store(self, version=0):
        raw_tweet_dataset_table_name = self.get_latest_raw_dataset_name(version=version)

        raw_tweet_dataset_df_deduplicated, test_df, dev_df, \
            snorkel_train_df, train_df = self.get_processed_datasets(version=version)

        dir_path = f"{os.path.expanduser('~')}/ssp/data/dump/{raw_tweet_dataset_table_name}" + "_mannual_annotated"
        check_n_mk_dirs(dir_path)

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=test_df,
                                 overwrite=self._overwrite,
                                 path=dir_path + "/test.parquet")

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=dev_df,
                                 overwrite=self._overwrite,
                                 path=dir_path + "/dev.parquet")

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        self.store_df_as_parquet(df=snorkel_train_df,
                                 overwrite=self._overwrite,
                                 path=dir_path + "/snorkel_train_df.parquet")


        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        self.store_df_as_parquet(train_df,
                                 overwrite=self._overwrite,
                                 path=dir_path + "/train.parquet")
