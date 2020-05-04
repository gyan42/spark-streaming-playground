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
from pyspark.sql.types import IntegerType
from sklearn.base import BaseEstimator, TransformerMixin
from pyspark.sql.functions import udf
from ssp.utils.ai_key_words import AIKeyWords


def labelme(text, keywords=AIKeyWords.POSITIVE.split("|")):
    text = text.replace("#", "").replace("@", "")
    res = 0
    for keyword in keywords:
        if f' {keyword.lower()} ' in f' {text.lower()} ':
            res = 1
    return res

labelme_udf = udf(labelme, IntegerType())

class SSPTextLabeler(BaseEstimator, TransformerMixin):
    def __init__(self, input_col=None, output_col="label"):
        self._input_col = input_col
        self._output_col = output_col

    # Return self nothing else to do here
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        if isinstance(X, pd.DataFrame):
            if self._input_col:
               X[self._output_col] = X[self._input_col].swifter.apply(lambda x: labelme(x, AIKeyWords.POSITIVE))
               print(X[self._output_col].value_counts())
               return X
        elif isinstance(X, list):
            X = [self.labelme(x, AIKeyWords.POSITIVE) for x in X]
            return X
        elif isinstance(X, str):
            return self.labelme(X, AIKeyWords.POSITIVE)
