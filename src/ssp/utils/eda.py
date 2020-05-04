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
from spacy.lang.en import STOP_WORDS
from wordcloud import STOPWORDS
from nltk.corpus import stopwords

from ssp.logger.pretty_print import print_info, print_warn, print_error


def get_value_count(df, label_col):
    return df[label_col].value_count()

def get_stop_words():
    words = list(STOPWORDS) + list(stopwords.words('english')) + list(STOP_WORDS)
    words = sorted(list(set(words)))
    words = [str(word) for word in words]
    return words