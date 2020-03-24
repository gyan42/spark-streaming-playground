import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer
import swifter
from ssp.utils.eda import get_stop_words
STOPWORDS = get_stop_words()


class TextFeatureEngineering(BaseEstimator, TransformerMixin):
    def __init__(self, input_col, output_col, max_features=4096, ngram_range=(2, 2)):
        self._input_col = input_col
        self._output_col = output_col
        self._cnt_vec = CountVectorizer(analyzer='word',
                                        stop_words=STOPWORDS,
                                        max_features=max_features,
                                        ngram_range=ngram_range)

    # Return self nothing else to do here
    def fit(self, X, y=None):
        self._cnt_vec = self._cnt_vec.fit(X[self._input_col])
        return self

    def get_features(self, text):
        return np.squeeze(self._cnt_vec.transform([text]).toarray())

    def transform(self, X, y=None):
        X[self._output_col] = X[self._input_col].swifter.apply(lambda x: self.get_features(x))
        X = np.array([np.array(xi) for xi in X[self._output_col].values])
        return X
