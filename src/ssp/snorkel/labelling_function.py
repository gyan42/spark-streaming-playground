import re
import pandas as pd
import gin
from sklearn.base import BaseEstimator, TransformerMixin

from snorkel.labeling import labeling_function
from snorkel.labeling import PandasLFApplier, LFApplier
from snorkel.labeling import LFAnalysis
from snorkel.labeling import LabelModel

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
                                     self.false_positive_tweets]

        self._pandas_applier = PandasLFApplier(lfs=self._labelling_functions)
        self._list_applier = LFApplier(lfs=self._labelling_functions)

        self._label_model = LabelModel(cardinality=2, verbose=True)

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
        return self._label_model.predict_proba(L=X)
    
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
    @labeling_function()
    def is_ai_tweet(x):
        if isinstance(x, str):
            return SSPTweetLabeller.POSITIVE if re.search(AIKeyWords.AI, x.lower()) else SSPTweetLabeller.ABSTAIN
        return SSPTweetLabeller.POSITIVE if re.search(AIKeyWords.AI, x.text.lower()) else SSPTweetLabeller.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_ml_tweet(x):
        if isinstance(x, str):
            return SSPTweetLabeller.POSITIVE if re.search(AIKeyWords.ML, x.lower()) else SSPTweetLabeller.ABSTAIN
        return SSPTweetLabeller.POSITIVE if not re.search(AIKeyWords.ML, x.text.lower()) else SSPTweetLabeller.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_dl_tweet(x):
        if isinstance(x, str):
            return SSPTweetLabeller.POSITIVE if re.search(AIKeyWords.DL, x.lower()) else SSPTweetLabeller.ABSTAIN
        return SSPTweetLabeller.POSITIVE if not re.search(AIKeyWords.DL, x.text.lower()) else SSPTweetLabeller.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_computer_vision_tweet(x):
        if isinstance(x, str):
            return SSPTweetLabeller.POSITIVE if re.search(AIKeyWords.CV, x.lower()) else SSPTweetLabeller.ABSTAIN
        return SSPTweetLabeller.POSITIVE if not re.search(AIKeyWords.CV, x.text.lower()) else SSPTweetLabeller.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_nlp_tweet(x):
        if isinstance(x, str):
            return SSPTweetLabeller.POSITIVE if re.search(AIKeyWords.NLP, x.lower()) else SSPTweetLabeller.ABSTAIN
        return SSPTweetLabeller.POSITIVE if not re.search(AIKeyWords.NLP, x.text.lower()) else SSPTweetLabeller.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_data_tweet(x):
        if isinstance(x, str):
            return SSPTweetLabeller.POSITIVE if re.search(AIKeyWords.DATA, x.lower()) else SSPTweetLabeller.ABSTAIN
        # print_info(x)
        return SSPTweetLabeller.POSITIVE if re.search(AIKeyWords.DATA, x.text.lower()) else SSPTweetLabeller.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_ai_hash_tags_tweet(x):
        if isinstance(x, str):
            return SSPTweetLabeller.POSITIVE if re.search(AIKeyWords.TWEET_HASH_TAGS, x.lower()) else SSPTweetLabeller.ABSTAIN
        # print_info(x)
        return SSPTweetLabeller.POSITIVE if re.search(AIKeyWords.TWEET_HASH_TAGS, x.text.lower()) else SSPTweetLabeller.ABSTAIN

    @staticmethod
    @labeling_function()
    def false_positive_tweets(x):
        if isinstance(x, str):
            return SSPTweetLabeller.POSITIVE if re.search(AIKeyWords.FALSE_POSITIVE, x.lower()) else SSPTweetLabeller.ABSTAIN
        return SSPTweetLabeller.NEGATIVE if not re.search(AIKeyWords.FALSE_POSITIVE, x.text.lower()) else SSPTweetLabeller.ABSTAIN


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
        raw_tweet_dataset_df_deduplicated, test_df, dev_df, snorkel_train_df, train_df = self.prepare_dataset()

        self._snorkel_labeler.fit(snorkel_train_df)
        self._snorkel_labeler.evaluate(test_df, test_df[self._label_output_column])
        res = self._snorkel_labeler.predict(train_df)
        print_info(res)

