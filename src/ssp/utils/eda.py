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