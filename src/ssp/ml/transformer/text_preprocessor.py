import re
import swifter
from sklearn.base import BaseEstimator, TransformerMixin
import spacy

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



class TextPreProcessor(BaseEstimator, TransformerMixin):
    def __init__(self, input_col, output_col):
        self._input_col = input_col
        self._output_col = output_col

    # Return self nothing else to do here
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X[self._output_col] = X[self._input_col].swifter.apply(preprocess)
        # Lematization ? for ML models
        # Tweets with more than 5 mentions/hashtag then consider it to be spam/useless, check with length
        return X

