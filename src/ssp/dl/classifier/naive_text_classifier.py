import os

import gin
import numpy as np
import pandas as pd
import tensorflow as tf
import spacy
import pickle
import pyarrow as pa
from ssp.logger.pretty_print import print_info, print_error
from ssp.utils.misc import check_n_mk_dirs

# https://stackoverflow.com/questions/55854885/unable-to-save-the-tensorflow-model-file-into-hdfs

@gin.configurable
class NaiveTextClassifier(object):
    def __init__(self,
                 train_df_or_path=None,
                 test_df_or_path=None,
                 dev_df_or_path=None,
                 model_dir=None,
                 wipe_old_data=False,
                 text_column="text",
                 label_column="label",
                 num_words=8000,
                 seq_len=128,
                 embedding_size=128,
                 batch_size=64,
                 hdfs_host=None,
                 hdfs_port=None):
        """

        :param train_df_or_path:
        :param test_df_or_path:
        :param dev_df_or_path:
        :param model_dir: Local directory path or HDFS path
        :param wipe_old_data:
        :param text_column:
        :param label_column:
        :param num_words:
        :param seq_len:
        :param embedding_size:
        :param batch_size:
        """
        self._pre_trained = False
        self._text_column = text_column
        self._label_column = label_column

        if isinstance(train_df_or_path, str):
            self._train_df, self._test_df, \
            self._dev_test = NaiveTextClassifier.load_parquet_data(train_file_path=train_df_or_path,
                                                                   test_file_path=test_df_or_path,
                                                                   dev_file_path=dev_df_or_path)
        else:
            self._train_df = train_df_or_path
            self._test_df = test_df_or_path
            self._dev_test = dev_df_or_path

        self.nlp = spacy.load("en_core_web_sm")
        self._num_words = num_words
        self._seq_len = seq_len
        self._embedding_size = embedding_size
        self._batch_size = batch_size
        self._epochs = 5
        self._threshold = 0.5
        self._train_seqs = None
        self._test_seqs = None
        self._model_name = "naive_text_classifier"
        self._model_dir = model_dir
        self._hdfs_host, self._hdfs_port = hdfs_host, hdfs_port

        if hdfs_host and hdfs_port:
            self._hdfs_fs = pa.hdfs.connect(hdfs_host, hdfs_port)
            self._is_local_dir = False

            self._model_path = f"{self._hdfs_port}/{self._model_dir}/{self._model_name}".replace("//", "/")
            self._model_path = f"hdfs://{self._hdfs_host}:" + self._model_path

            if self._hdfs_fs.exists(self._model_dir + 'tokenizer.pickle'):
                print_info(f"Loading tokenizer... {self._model_dir + 'tokenizer.pickle'}")
                with self._hdfs_fs.open(self._model_dir + 'tokenizer.pickle', 'rb') as f:
                    self._tokenizer = pickle.load(f)
            else:
                self._tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=self._num_words, oov_token='<UNK>')

            if self._hdfs_fs.exists(self._model_dir + self._model_name):
                self._pre_trained = True
                print_info(f"Loading model...{self._model_path}")
                self._model = tf.keras.models.load_model(self._model_path)
            else:
                self._model = self.get_model()
        else:
            check_n_mk_dirs(model_dir, is_remove=wipe_old_data)
            if os.path.exists(self._model_dir + 'tokenizer.pickle'):
                print_info(f"Loading tokenizer... {self._model_dir + 'tokenizer.pickle'}")
                with open(self._model_dir + 'tokenizer.pickle', 'rb') as f:
                    self._tokenizer = pickle.load(f)
            else:
                self._tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=self._num_words, oov_token='<UNK>')

            if os.path.exists(self._model_dir + self._model_name):
                self._pre_trained = True
                print_info(f"Loading model...{self._model_dir + self._model_name}")
                self._model = tf.keras.models.load_model(self._model_dir + self._model_name)
            else:
                self._model = self.get_model()

            self._hdfs_fs = None
            self._is_local_dir = True

    @staticmethod
    def load_parquet_data(train_file_path, test_file_path, dev_file_path):
        return pd.read_parquet(train_file_path, engine="fastparquet"), \
               pd.read_parquet(test_file_path, engine="fastparquet"), \
               pd.read_parquet(dev_file_path, engine="fastparquet")

    def fit_tokenizer(self):
        if self._train_df is not None:
            # create tokenizer for our data
            self._tokenizer.fit_on_texts(self._train_df[self._text_column])
        else:
            print_info("No data for training!")

    def transform(self, text_list):
        # convert text data to numerical indexes
        seqs = self._tokenizer.texts_to_sequences(text_list)
        # pad data up to SEQ_LEN (note that we truncate if there are more than SEQ_LEN tokens)
        seqs = tf.keras.preprocessing.sequence.pad_sequences(seqs, maxlen=self._seq_len, padding="post")
        return seqs

    def preprocess_train_data(self):
        if self._train_df is not None:
            self.fit_tokenizer()
            self._train_seqs = self.transform(text_list=self._train_df[self._text_column])
            self._test_seqs = self.transform(text_list=self._test_df[self._text_column])
        else:
            print_info("No data for training!")


    def get_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Embedding(self._num_words, self._embedding_size),
            tf.keras.layers.GlobalAveragePooling1D(),
            tf.keras.layers.Dense(1, activation='sigmoid')])

        model.summary()

        model.compile(optimizer='adam',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])
        return model

    def train(self):
        if self._pre_trained:
            return True
        es = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max')
        callbacks = [es]
        print_error(self._train_seqs)
        history = self._model.fit(self._train_seqs,
                                  self._train_df[self._label_column].values,
                                  batch_size=self._batch_size,
                                  epochs=self._epochs,
                                  validation_split=0.2,
                                  callbacks=callbacks)

    def evaluate(self):
        res = self._model.evaluate(self._test_seqs, self._test_df[self._label_column].values)[1]
        print(res)

    def save_model(self):
        if self._is_local_dir:
            if os.path.exists(self._model_dir + self._model_name):
                return
            self._model.save(self._model_dir + self._model_name)
            with open(self._model_dir + 'tokenizer.pickle', 'wb') as handle:
                pickle.dump(self._tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            if self._hdfs_fs.exists(self._model_path):
                return
            print_info(f"Saving model to {self._model_path}")
            self._model.save(self._model_path)
            with self._hdfs_fs.open(self._model_dir + 'tokenizer.pickle', 'wb') as handle:
                pickle.dump(self._tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def predict(self, X):
        if isinstance(X, list) or isinstance(X, np.ndarray):
            seqs = self.transform(text_list=X)
            preds = self._model.predict(seqs)
            return preds
        elif isinstance(X, pd.DataFrame):
            X["prediction"] = self.transform(text_list=X["text"])
            return X
        elif isinstance(X, str):
            res = self.transform([X])
            return res[0]

