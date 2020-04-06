import re
import pandas as pd
import gin
from sklearn.base import BaseEstimator, TransformerMixin
import nltk

from snorkel.labeling import labeling_function
from snorkel.labeling import PandasLFApplier, LFApplier
from snorkel.labeling import LFAnalysis
from snorkel.labeling import LabelModel

from ssp.logger.pretty_print import print_error
from ssp.logger.pretty_print import print_info
from ssp.posgress.dataset_base import PostgresqlDatasetBase
from ssp.snorkel.ai_key_words import AIKeyWords

class SSPTweetLabeller(BaseEstimator, TransformerMixin):
    # Set voting values.
    # all other tweets
    ABSTAIN = -1
    # tweets that talks about science, AI, data
    POSITIVE = 1
    # tweets that are not
    NEGATIVE = 0

    def __init__(self):
        self._labelling_functions = [self.is_ai_tweet,
                                     self.is_ml_tweet,
                                     self.is_dl_tweet,
                                     self.is_computer_vision_tweet,
                                     self.is_nlp_tweet,
                                     self.is_data_tweet,
                                     self.is_ai_hash_tags_tweet,
                                     self.not_data_science,
                                     self.not_neural_network]

        self._pandas_applier = PandasLFApplier(lfs=self._labelling_functions)
        self._list_applier = LFApplier(lfs=self._labelling_functions)

        self._label_model = LabelModel(cardinality=2, verbose=True, )

    def fit(self, X, y=None):
        if isinstance(X, str):
            X = [X]

        if isinstance(X, pd.DataFrame):
            X_labels = self._pandas_applier.apply(X)
            print_info(LFAnalysis(L=X_labels, lfs=self._labelling_functions).lf_summary())
            self._label_model.fit(L_train=X_labels, n_epochs=500, log_freq=100, seed=42)
        elif isinstance(X, list):
            X_labels = self._list_applier.apply(X)
            print_info(LFAnalysis(L=X_labels, lfs=self._labelling_functions).lf_summary())
            self._label_model.fit(L_train=X_labels, n_epochs=500, log_freq=100, seed=42)
        else:
            raise RuntimeError("Unknown type...")
        
        return self

    def predict(self, X):
        return self._label_model.predict_proba(L=self._list_applier.apply(X))
    
    def evaluate(self, X, y):
        if isinstance(X, list):
            X_labels = self._list_applier.apply(X)
            label_model_acc = self._label_model.score(L=X_labels, Y=y, tie_break_policy="random")[
                "accuracy"
            ]
            print(f"{'Label Model Accuracy:':<25} {label_model_acc * 100:.1f}%")
        elif isinstance(X, pd.DataFrame):
            X_labels = self._pandas_applier.apply(X)
            label_model_acc = self._label_model.score(L=X_labels, Y=y, tie_break_policy="random")[
                "accuracy"
            ]
            print(f"{'Label Model Accuracy:':<25} {label_model_acc * 100:.1f}%")
        else:
            raise RuntimeError("Unknown type...")

    @staticmethod
    def positive_search(data, key_words):
        if not isinstance(data, str):
            data = data.text #Dataframe series

        data = data.replace("#", "").replace("@", "")
        for keyword in key_words:
            if f' {keyword.lower()} ' in f' {data.lower()} ':
                # print_info(data)
                return SSPTweetLabeller.POSITIVE
        return SSPTweetLabeller.ABSTAIN

    @staticmethod
    def negative_search(data, key_words):
        if not isinstance(data, str):
            data = data.text #Dataframe series

        data = data.replace("#", "").replace("@", "")
        for keyword in key_words:
            if f' {keyword.lower()} ' in f' {data.lower()} ':
                # print_error(data)
                return SSPTweetLabeller.NEGATIVE
        return SSPTweetLabeller.ABSTAIN


    @staticmethod
    @labeling_function()
    def is_ai_tweet(x):
        return SSPTweetLabeller.positive_search(x, AIKeyWords.AI.split("|"))

    @staticmethod
    @labeling_function()
    def is_ml_tweet(x):
        return SSPTweetLabeller.positive_search(x, AIKeyWords.ML.split("|"))

    @staticmethod
    @labeling_function()
    def is_dl_tweet(x):
        return SSPTweetLabeller.positive_search(x, AIKeyWords.DL.split("|"))

    @staticmethod
    @labeling_function()
    def is_computer_vision_tweet(x):
        return SSPTweetLabeller.positive_search(x, AIKeyWords.CV.split("|"))

    @staticmethod
    @labeling_function()
    def is_nlp_tweet(x):
        return SSPTweetLabeller.positive_search(x, AIKeyWords.NLP.split("|"))

    @staticmethod
    @labeling_function()
    def is_data_tweet(x):
        return SSPTweetLabeller.positive_search(x, AIKeyWords.DATA.split("|"))

    @staticmethod
    @labeling_function()
    def is_ai_hash_tags_tweet(x):
        return SSPTweetLabeller.positive_search(x, AIKeyWords.TWEET_HASH_TAGS.split("|"))

    # @staticmethod
    # @labeling_function()
    # def false_positive_tweets(x):
    #     return SSPTweetLabeller.negative_search(x, AIKeyWords.FALSE_POSITIVE.split("|"))

    @staticmethod
    @labeling_function()
    def not_data_science(x):
        if not isinstance(x, str):
            x = x.text
        # Get bigrams and check whetehr there is data science or not
        bigrm = list(nltk.bigrams(x.split()))
        bigrm = list(map(' '.join, bigrm))
        for pair in bigrm:
            if "science" in pair and "data" not in pair:
                # print_error(x)
                return SSPTweetLabeller.NEGATIVE
        else:
            return SSPTweetLabeller.ABSTAIN


    @staticmethod
    @labeling_function()
    def not_neural_network(x):
        if not isinstance(x, str):
            x = x.text
        # Get bigrams and check whetehr there is data science or not
        bigrm = list(nltk.bigrams(x.split()))
        bigrm = list(map(' '.join, bigrm))
        for pair in bigrm:
            if "network" in pair and "neural" not in pair:
                # print_error(x)
                return SSPTweetLabeller.NEGATIVE
        else:
            return SSPTweetLabeller.ABSTAIN

@gin.configurable
class SSPPostgresqlTweetLabelling(PostgresqlDatasetBase):
    def __init__(self,
                 snorker_label_column="snorkel_label",
                 text_column="text",
                 label_output_column="naive_label",
                 raw_tweet_table_name_prefix="raw_tweet_dataset",
                 postgresql_host="localhost",
                 postgresql_port="5432",
                 postgresql_database="sparkstreamingdb",
                 postgresql_user="sparkstreaming",
                 postgresql_password="sparkstreaming"):

        PostgresqlDatasetBase.__init__(self,
                                       text_column=text_column,
                                       label_output_column=label_output_column,
                                       raw_tweet_table_name_prefix=raw_tweet_table_name_prefix,
                                       postgresql_host=postgresql_host,
                                       postgresql_port=postgresql_port,
                                       postgresql_database=postgresql_database,
                                       postgresql_user=postgresql_user,
                                       postgresql_password=postgresql_password)

        self._snorkel_labeler = SSPTweetLabeller()
        self._snorker_label_column = snorker_label_column

    def run_labeler(self):
        raw_tweet_dataset_df_deduplicated, test_df, dev_df, snorkel_train_df, train_df = self.get_processed_datasets()

        self._snorkel_labeler.fit(snorkel_train_df)
        self._snorkel_labeler.evaluate(test_df, test_df[self._label_output_column])
        # res = self._snorkel_labeler.predict(train_df[self._text_column])
        # print_info(res[:, 0])

