from sklearn.base import BaseEstimator, TransformerMixin
from ssp.utils.configuration import StreamingConfigs


class SSPTextLabeler(BaseEstimator, TransformerMixin):
    def __init__(self, config_file_path, input_col, output_col="label"):
        self._input_col = input_col
        self._output_col = output_col
        self._config = StreamingConfigs(config_file_path=config_file_path, twitter_ini_file=None)

    # Return self nothing else to do here
    def fit(self, X, y=None):
        return self

    def labelme(self, text, keyboards):
        res = 0
        for keyword in keyboards:
            if keyword.lower() in text:
                res = 1
        return res

    def transform(self, X, y=None):
        X[self._output_col] = X[self._input_col].apply(lambda x: self.labelme(x, self._config._key_words))
        print(X[self._output_col].value_counts())
        return X