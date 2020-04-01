import re
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

from snorkel.labeling import labeling_function
from snorkel.labeling import LabelModel, PandasLFApplier
from snorkel.labeling import PandasLFApplier
from snorkel.labeling import LFAnalysis
from snorkel.labeling import LabelModel

from ssp.logger.pretty_print import print_info
from ssp.posgress.dataset_base import PostgresqlDatasetBase
from ssp.snorkel.ai_key_words import AIKeyWords
from ssp.ml.transformer import SSPTextLabeler

class SSPTweetLabelling(BaseEstimator, TransformerMixin, PostgresqlDatasetBase):
    # Set voting values.
    # all other tweets
    ABSTAIN = -1
    # tweets that talks about science, AI, data
    POSITIVE = 1
    # tweets that are not
    NEGATIVE = 0

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

        self._labelling_functions = [self.is_ai_tweet,
                                     self.is_ml_tweet,
                                     self.is_dl_tweet,
                                     self.is_computer_vision_tweet,
                                     self.is_nlp_tweet,
                                     self.is_data_tweet,
                                     self.is_ai_hash_tags_tweet,
                                     self.false_positive_tweets]

        self._applier = PandasLFApplier(lfs=self._labelling_functions)


    @staticmethod
    @labeling_function()
    def is_ai_tweet(x):
        return SSPTweetLabelling.POSITIVE if re.search(AIKeyWords.AI, x.text.lower()) else SSPTweetLabelling.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_ml_tweet(x):
        return SSPTweetLabelling.POSITIVE if not re.search(AIKeyWords.ML, x.text.lower()) else SSPTweetLabelling.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_dl_tweet(x):
        return SSPTweetLabelling.POSITIVE if not re.search(AIKeyWords.DL, x.text.lower()) else SSPTweetLabelling.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_computer_vision_tweet(x):
        return SSPTweetLabelling.POSITIVE if not re.search(AIKeyWords.CV, x.text.lower()) else SSPTweetLabelling.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_nlp_tweet(x):
        return SSPTweetLabelling.POSITIVE if not re.search(AIKeyWords.NLP, x.text.lower()) else SSPTweetLabelling.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_data_tweet(x):
        # print_info(x)
        return SSPTweetLabelling.POSITIVE if re.search(AIKeyWords.DATA, x.text.lower()) else SSPTweetLabelling.ABSTAIN

    @staticmethod
    @labeling_function()
    def is_ai_hash_tags_tweet(x):
        # print_info(x)
        return SSPTweetLabelling.POSITIVE if re.search(AIKeyWords.TWEET_HASH_TAGS, x.text.lower()) else SSPTweetLabelling.ABSTAIN

    @staticmethod
    @labeling_function()
    def false_positive_tweets(x):
        return SSPTweetLabelling.NEGATIVE if not re.search(AIKeyWords.FALSE_POSITIVE, x.text.lower()) else SSPTweetLabelling.ABSTAIN

    def label_applier(self):
        self._lf_train_labels = self._applier.apply(df=self._lf_dataset)
        L_test = self._applier.apply(df=self._test_dataset)
        L_val = self._applier.apply(df=self._dev_dataset)

    def train(self):
        Y_test = self._test_dataset["label_annotated"].values

        print_info(LFAnalysis(L=L_train, lfs=self._labelling_functions).lf_summary())

        label_model = LabelModel(cardinality=2, verbose=True)
        label_model.fit(L_train=L_train, n_epochs=500, log_freq=100, seed=42)

        label_model_acc = label_model.score(L=L_test, Y=Y_test, tie_break_policy="random")[
            "accuracy"
        ]
        print(f"{'Label Model Accuracy:':<25} {label_model_acc * 100:.1f}%")

