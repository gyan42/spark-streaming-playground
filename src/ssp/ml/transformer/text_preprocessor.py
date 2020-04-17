#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import re
import pandas as pd
import swifter
from pyspark.sql.types import StringType
from sklearn.base import BaseEstimator, TransformerMixin
import spacy
from tqdm import tqdm
from pyspark.sql.functions import udf
from ssp.utils.eda import get_stop_words
STOPWORDS = get_stop_words()

nlp = spacy.load('en_core_web_sm')


def remove_stop_words(text):
    res = []
    for token in nlp(text):
        # Remove mentions and numeric words, added after checking vectorizer terms/vocabs
        if token.text not in STOPWORDS and not token.text.startswith("\u2066@") and\
                not token.text.startswith("@") and\
                re.search('[a-zA-Z]', token.text): #filter only words with alphabets
            res.append(token.lemma_.strip())
    res = " ".join(res)
    return res


def preprocess(text):
    # Remove https links, added after visualizing in wordcloud plot
    text = re.sub("http[s]?:\/\/\S+", "", text.strip())
    # General strategy for ML algos
    text = remove_stop_words(text=text)
    # Remove punctuation
    text = re.sub('[^a-zA-Z0-9\s]', '', text)
    text = text.lower()
    text = text.replace("\n", " ")
    return text.strip()


preprocess_udf = udf(preprocess, StringType())


class TextPreProcessor(BaseEstimator, TransformerMixin):
    def __init__(self, input_col=None, output_col=None):
        self._input_col = input_col
        self._output_col = output_col

    # Return self nothing else to do here
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        if isinstance(X, pd.DataFrame):
            if self._output_col:
                X[self._output_col] = X[self._input_col].swifter.apply(preprocess)
            return X
        elif isinstance(X, list):
            X = [preprocess(x) for x in tqdm(X)]
            return X
        elif isinstance(X, str):
            return preprocess(X)

        # Lematization ? for ML models
        # Tweets with more than 5 mentions/hashtag then consider it to be spam/useless, check with length
        return X

