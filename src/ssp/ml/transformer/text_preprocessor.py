import re
import swifter
from sklearn.base import BaseEstimator, TransformerMixin

from ssp.utils.eda import get_stop_words
STOPWORDS = get_stop_words()


class TextPreProcessor(BaseEstimator, TransformerMixin):
    def __init__(self, input_col, output_col):
        self._input_col = input_col
        self._output_col = output_col

    # Return self nothing else to do here
    def fit(self, X, y=None):
        return self

    def remove_stop_words(self, text):
        res = []
        for word in text.split(" "):
            if word not in STOPWORDS and not word.startswith("\u2066@"):
                    res.append(word)
        res = " ".join(res)
        return res

    def transform(self, X, y=None):
        # Remove https links
        X[self._output_col] = X[self._input_col].swifter.apply(lambda x: re.sub("http[s]?:\/\/\S+", "", x))
        X[self._output_col] = X[self._output_col].swifter.apply(lambda x: self.remove_stop_words(x))
        # # Remove punctuation
        X[self._output_col] = X[self._output_col].swifter.apply(lambda x: re.sub('[^a-zA-Z0-9\s]', '', x))
        # # To smaller
        X[self._output_col] = X[self._output_col].swifter.apply(lambda x: x.lower())
        X[self._output_col] = X[self._output_col].swifter.apply(lambda x: x.replace("\n", " "))
        # Remove stop words ? for ML models
        # Lematization ? for ML models
        # Remove mentions
        # Tweets with more than 5 mentions/hashtag then consider it to be spam/useless, check with length
        return X

