#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import pandas as pd
import gin
from sklearn.base import BaseEstimator, TransformerMixin
import nltk

from snorkel.labeling import labeling_function
from snorkel.labeling import LFApplier
from snorkel.labeling import LFAnalysis
from snorkel.labeling import LabelModel

from ssp.logger.pretty_print import print_error
from ssp.logger.pretty_print import print_info
from ssp.posgress.dataset_base import PostgresqlDatasetBase
from ssp.utils.ai_key_words import AIKeyWords


class SSPTweetLabeller(BaseEstimator, TransformerMixin):
    """
    Snorkel Transformer uses LFs to train a Label Model, that can annotate AI text and non AI text
    :param input_col: Name of the input text column if Dataframe is used
    :param output_col: Name of the ouput label column if Dataframe is used
    """
    # Set voting values.
    # all other tweets
    ABSTAIN = -1
    # tweets that talks about science, AI, data
    POSITIVE = 1
    # tweets that are not
    NEGATIVE = 0

    def __init__(self,
                 input_col="text",
                 output_col="slabel"):

        # LFs needs to be static or normal function
        self._labelling_functions = [self.is_ai_tweet,
                                     self.is_not_ai_tweet,
                                     self.not_data_science,
                                     self.not_neural_network,
                                     self.not_big_data,
                                     self.not_nlp,
                                     self.not_ai,
                                     self.not_cv]

        self._input_col = input_col
        self._output_col = output_col
        self._list_applier = LFApplier(lfs=self._labelling_functions)

        self._label_model = LabelModel(cardinality=2, verbose=True)

    def fit(self, X, y=None):
        """

        :param X: (Dataframe) / (List) Input text
        :param y: None
        :return: Numpy Array [num of samples, num of LF functions]
        """
        if isinstance(X, str):
            X = [X]

        if isinstance(X, pd.DataFrame):
            text_list = X[self._input_col]
            X_labels = self._list_applier.apply(text_list)
            print_info(LFAnalysis(L=X_labels, lfs=self._labelling_functions).lf_summary())
            print_info("Training LabelModel")
            self._label_model.fit(L_train=X_labels, n_epochs=500, log_freq=100, seed=42)
        elif isinstance(X, list):
            X_labels = self._list_applier.apply(X)
            print_info(LFAnalysis(L=X_labels, lfs=self._labelling_functions).lf_summary())
            print_info("Training LabelModel")
            self._label_model.fit(L_train=X_labels, n_epochs=500, log_freq=100, seed=42)
        else:
            raise RuntimeError("Unknown type...")
        
        return self

    def normalize_prob(self, res):
        return [1 if r > 0.5 else 0 for r in res]

    def transform(self, X, y=None):
        if isinstance(X, pd.DataFrame):
            if self._input_col:
               res = self.predict(X[self._input_col])[:, 1]
               X[self._output_col] = self.normalize_prob(res)
               return X
        elif isinstance(X, list):
            res = self.predict(X)[:, 1]
            return self.normalize_prob(res)
        elif isinstance(X, str):
            res = self.predict([X])[:, 1]
            return self.normalize_prob(res)[0]

    def predict(self, X):
        return self._label_model.predict_proba(L=self._list_applier.apply(X))
    
    def evaluate(self, X, y):
        if isinstance(X, list):
            X_labels = self._list_applier.apply(X)
            label_model_acc = self._label_model.score(L=X_labels, Y=y, tie_break_policy="random")[
                "accuracy"
            ]
            print_info(LFAnalysis(L=X_labels, lfs=self._labelling_functions).lf_summary())
            print(f"{'Label Model Accuracy:':<25} {label_model_acc * 100:.1f}%")
        elif isinstance(X, pd.DataFrame):
            text_list = X[self._input_col]
            X_labels = self._list_applier.apply(text_list)
            label_model_acc = self._label_model.score(L=X_labels, Y=y, tie_break_policy="random")[
                "accuracy"
            ]
            print(f"{'Label Model Accuracy:':<25} {label_model_acc * 100:.1f}%")
        else:
            raise RuntimeError("Unknown type...")

    @staticmethod
    def positive_search(data, key_words):
        data = data.replace("#", "").replace("@", "")
        for keyword in key_words:
            if f' {keyword.lower()} ' in f' {data.lower()} ':
                return SSPTweetLabeller.POSITIVE
        return SSPTweetLabeller.ABSTAIN

    @staticmethod
    def negative_search(data, positive_keywords, false_positive_keywords):
        data = data.replace("#", "").replace("@", "")

        positive = False
        false_positive = False
        for keyword in positive_keywords:
            if f' {keyword.lower()} ' in f' {data.lower()} ':
                positive = True

        for keyword in false_positive_keywords:
            if f' {keyword.lower()} ' in f' {data.lower()} ':
                false_positive = True

        if false_positive and not positive:
            # print_info(data)
            return SSPTweetLabeller.NEGATIVE

        return SSPTweetLabeller.ABSTAIN

    @staticmethod
    def bigram_check(x, word1, word2):
        # Get bigrams and check tuple exists or not
        bigrm = list(nltk.bigrams(x.split()))
        bigrm = list(map(' '.join, bigrm))
        count = 0
        for pair in bigrm:
            if word1 in pair and word2 not in pair:
                count += 1
        if count > 0:
            return SSPTweetLabeller.NEGATIVE
        else:
            return SSPTweetLabeller.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_ai_tweet(x):
        return SSPTweetLabeller.positive_search(x, AIKeyWords.POSITIVE.split("|"))

    @staticmethod
    @labeling_function()
    def is_not_ai_tweet(x):
        return SSPTweetLabeller.negative_search(data=x,
                                                positive_keywords=AIKeyWords.POSITIVE.split("|"),
                                                false_positive_keywords=AIKeyWords.FALSE_POSITIVE.split("|"))

    @staticmethod
    @labeling_function()
    def not_data_science(x):
        return SSPTweetLabeller.bigram_check(x, "data", "science")

    @staticmethod
    @labeling_function()
    def not_neural_network(x):
        return SSPTweetLabeller.bigram_check(x, "neural", "network")

    @staticmethod
    @labeling_function()
    def not_big_data(x):
        return SSPTweetLabeller.bigram_check(x, "big", "data")

    @staticmethod
    @labeling_function()
    def not_nlp(x):
        return SSPTweetLabeller.bigram_check(x, "natural", "language")

    @staticmethod
    @labeling_function()
    def not_ai(x):
        return SSPTweetLabeller.bigram_check(x, "artificial", "intelligence")

    @staticmethod
    @labeling_function()
    def not_cv(x):
        return SSPTweetLabeller.bigram_check(x, "computer", "vision")


@gin.configurable
class SSPLabelEvaluator(PostgresqlDatasetBase):

    def __init__(self,
                 text_column="text",
                 label_column="label",
                 raw_tweet_table_name_prefix="raw_tweet_dataset",
                 postgresql_host="localhost",
                 postgresql_port="5432",
                 postgresql_database="sparkstreamingdb",
                 postgresql_user="sparkstreaming",
                 postgresql_password="sparkstreaming"):

        PostgresqlDatasetBase.__init__(self,
                                       text_column=text_column,
                                       label_output_column=label_column,
                                       raw_tweet_table_name_prefix=raw_tweet_table_name_prefix,
                                       postgresql_host=postgresql_host,
                                       postgresql_port=postgresql_port,
                                       postgresql_database=postgresql_database,
                                       postgresql_user=postgresql_user,
                                       postgresql_password=postgresql_password)

        self._snorkel_labeler = SSPTweetLabeller()

    def run_labeler(self, version=0):
        raw_tweet_dataset_df_deduplicated, test_df, dev_df, \
                snorkel_train_df, train_df = self.get_processed_datasets(version=version)
        self._snorkel_labeler.fit(snorkel_train_df)
        self._snorkel_labeler.evaluate(test_df, test_df[self._label_output_column])

        # snorkel_train_df["label"] = snorkel_train_df["text"].apply(lambda x: SSPTweetLabeller.is_ai_tweet(x))
        # print_info(snorkel_train_df["label"].value_counts())
        # print_error(snorkel_train_df[snorkel_train_df["label"]==0]["text"].tolist()[:10])

        # print_info(snorkel_train_df[snorkel_train_df["label"]==1]["text"].tolist()[:10])

        # res = self._snorkel_labeler.predict(train_df[self._text_column])
        # res = res[:, 1]
        # res = [1 if r >= 0.5 else 0 for r in res]
        # print_error(train_df.shape[0])
        # print_info(sum(res))
        # train_df["snorkel_label"] = res
        # for label, group in train_df[["text", "snorkel_label"]].groupby("snorkel_label"):
        #     if label == 1:
        #         print(label)
        #         print_info(group.shape[0])
        #         group.reset_index(inplace=True)
        #         # print_info("\n".join(group["text"].tolist()[:10]))
        #         group["label"] = group["text"].apply(lambda x: SSPTweetLabeller.is_ai_tweet(x))
        #         print_info("\n".join(group[group["label"]==1]["text"].tolist()[:100]))

