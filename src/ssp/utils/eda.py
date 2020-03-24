import pandas as pd
from wordcloud import STOPWORDS
from nltk.corpus import stopwords


def get_value_count(df, label_col):
    return df[label_col].value_count()

def get_stop_words():
    return STOPWORDS.union(stopwords.words('english')).union(["let"])