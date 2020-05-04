#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import swifter
from ssp.utils.eda import get_stop_words
STOPWORDS = get_stop_words()


class TextFeatureEngineering(BaseEstimator, TransformerMixin):
    def __init__(self, input_col, output_col, vectorizer="count", max_features=2*24, ngram_range=(2,2)):
        self._input_col = input_col
        self._output_col = output_col
        if vectorizer == "count":
            self._vec = CountVectorizer(analyzer='word',
                                        stop_words=STOPWORDS,
                                        max_features=max_features,
                                        ngram_range=ngram_range)
        elif vectorizer == "tfidf":
            self._vec = TfidfVectorizer(stop_words='english')

    def get_feature_names(self):
        return self._vec.get_feature_names()

    # Return self nothing else to do here
    def fit(self, X, y=None):
        self._vec = self._vec.fit(X[self._input_col])
        return self

    def get_features(self, text):
        return np.squeeze(self._vec.transform([text]).toarray())

    def transform(self, X, y=None):
        X[self._output_col] = X[self._input_col].swifter.apply(lambda x: self.get_features(x))
        X = np.array([np.array(xi) for xi in X[self._output_col].values])
        return X
