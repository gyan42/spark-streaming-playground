#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import os

import gin
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.callbacks import Callback
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.metrics import classification_report

import spacy
import pickle
import pyarrow as pa
from ssp.logger.pretty_print import print_info, print_error
from ssp.utils.misc import check_n_mk_dirs


# https://stackoverflow.com/questions/55854885/unable-to-save-the-tensorflow-model-file-into-hdfs
# https://towardsdatascience.com/a-gentle-introduction-to-apache-arrow-with-apache-spark-and-pandas-bb19ffe0ddae
# https://tech.marksblogg.com/working-with-hdfs.html
# https://towardsdatascience.com/a-gentle-introduction-to-apache-arrow-with-apache-spark-and-pandas-bb19ffe0ddae
# https://www.bmc.com/blogs/keras-neural-network-classification/
@gin.configurable
class NaiveTextClassifier(object):
    """
    Trains simple DL model with embedding and feed forward network
    HDFS will be considered for storage if HDFS host and port are given

    :param train_df_or_path: Train data pandas dataframe or path
    :param test_df_or_path: Test data pandas dataframe or path
    :param dev_df_or_path: Dev data pandas dataframe or path
    :param model_root_dir: Local directory path or HDFS path
    :param wipe_old_data: Clean old model data
    :param text_column: Name of the text column
    :param label_column: Name of the label colum
    :param num_words: Vocab size
    :param seq_len: Max length of the sequence
    :param embedding_size: Embedding size
    :param batch_size: Train batch size
    :param hdfs_host: HDFS host
    :param hdfs_port: HDFS port
    """

    def __init__(self,
                 train_df_or_path=None,
                 test_df_or_path=None,
                 dev_df_or_path=None,
                 model_root_dir=None,
                 model_version=1,
                 wipe_old_data=False,
                 text_column="text",
                 label_column="label",
                 num_words=8000,
                 seq_len=128,
                 embedding_size=64,
                 batch_size=64,
                 hdfs_host=None,
                 hdfs_port=None):

        self._pre_trained = False
        self._text_column = text_column
        self._label_column = label_column

        if isinstance(train_df_or_path, str):
            self._train_df, self._test_df, \
            self._dev_df = NaiveTextClassifier.load_parquet_data(train_file_path=train_df_or_path,
                                                                 test_file_path=test_df_or_path,
                                                                 dev_file_path=dev_df_or_path)
        else:
            self._train_df = train_df_or_path
            self._test_df = test_df_or_path
            self._dev_df = dev_df_or_path

        self.nlp = spacy.load("en_core_web_sm")
        self._num_words = num_words
        self._seq_len = seq_len
        self._embedding_size = embedding_size
        self._batch_size = batch_size
        self._epochs = 5
        self._threshold = 0.5
        self._train_seqs = None
        self._dev_seqs = None
        self._test_seqs = None
        self._model_name = "naive_text_classifier"
        self._model_version = model_version
        self._hdfs_host, self._hdfs_port = hdfs_host, hdfs_port
        self._wipe_old_data = wipe_old_data

        if model_root_dir:
            self._model_dir_ = os.path.expanduser(model_root_dir) + "/" + self._model_name + "/" + str(self._model_version) + "/"
            self._model_dir =self._model_dir_.replace("//", "/")
            self._model_export_dir = os.path.expanduser(model_root_dir) + "/" + self._model_name + "/exported/" + str(self._model_version) + "/"

        # Format the path for HDFS storage
        if hdfs_host and hdfs_port:
            self._model_dir = f"{self._hdfs_port}/{self._model_dir}".replace("//", "/")
            self._model_dir = f"hdfs://{self._hdfs_host}:" + self._model_dir

            self._model_export_dir = f"{self._hdfs_port}/{self._model_export_dir}".replace("//", "/")
            self._model_export_dir = f"hdfs://{self._hdfs_host}:" + self._model_export_dir

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
            self._dev_seqs = self.transform(text_list=self._dev_df[self._text_column])
            self._test_seqs = self.transform(text_list=self._test_df[self._text_column])
        else:
            print_info("No data for training!")

    def define_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.Embedding(self._num_words, self._embedding_size),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(self._embedding_size)),
            # tf.keras.layers.GlobalAveragePooling1D(),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(2, activation='softmax')], name="naive_rnn_classifier")

        model.summary()

        model.compile(optimizer='adam',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    def train(self):
        if self._pre_trained:
            return True
        # metrics = Metrics()


        es = tf.keras.callbacks.EarlyStopping(monitor='val_accuracy', mode='max')
        callbacks = [es]
        history = self._model.fit(self._train_seqs,
                                  to_categorical(self._train_df[self._label_column].values),
                                  batch_size=self._batch_size,
                                  epochs=self._epochs,
                                  validation_data=(self._dev_seqs, to_categorical(self._dev_df[self._label_column].values)),
                                  # validation_split=0.2,
                                  callbacks=callbacks)

    def evaluate(self):
        # print_info("\n".join(self._test_df[self._test_df[self._label_column] == 1][self._text_column].tolist()))
        # res = self._model.evaluate(self._test_seqs, self._test_df[self._label_column].values)[1]
        # print(res)
        y_pred = self._model.predict(self._test_seqs, batch_size=64, verbose=1)
        # print(y_pred)

        y_pred_bool = np.argmax(y_pred, axis=1)

        print(classification_report(self._test_df[self._label_column].values, y_pred_bool))

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

    def load_tokenizer(self, tokenizer_path=None):
        """
        Loads model and tokenizer.
        Loads from HDFS if host and port number are available or local file system is used.

        :return:
        """
        if tokenizer_path is None:
            tokenizer_path = self._model_dir
        else:
            tokenizer_path = os.path.expanduser(tokenizer_path)

        # If HDFS host and port number are
        if self._hdfs_host and self._hdfs_port:
            self._hdfs_fs = pa.hdfs.connect(self._hdfs_host, self._hdfs_port)
            self._is_local_dir = False

            if self._hdfs_fs.exists(tokenizer_path + 'tokenizer.pickle'):
                print_info(f"Loading tokenizer... {self._model_dir + 'tokenizer.pickle'}")
                with self._hdfs_fs.open(tokenizer_path + 'tokenizer.pickle', 'rb') as f:
                    self._tokenizer = pickle.load(f)
            else:
                self._tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=self._num_words, oov_token='<UNK>')
        else:
            if os.path.exists(tokenizer_path + 'tokenizer.pickle'):
                print_info(f"Loading tokenizer... {tokenizer_path + 'tokenizer.pickle'}")
                with open(tokenizer_path + 'tokenizer.pickle', 'rb') as f:
                    self._tokenizer = pickle.load(f)
            else:
                self._tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=self._num_words, oov_token='<UNK>')

            self._hdfs_fs = None
            self._is_local_dir = True

    def load_model(self):
        """
        Loads models
        Loads from HDFS if host and port number are available or local file system is used.

        :return:
        """
        # If HDFS host and port number are
        if self._hdfs_host and self._hdfs_port:
            self._hdfs_fs = pa.hdfs.connect(self._hdfs_host, self._hdfs_port)
            self._is_local_dir = False

            if self._hdfs_fs.exists(self._model_dir):
                self._pre_trained = True
                print_info(f"Loading model from HDFS...{self._model_dir}")
                self._model = tf.keras.models.load_model(self._model_dir)
            else:
                self._model = self.define_model()
        else:
            if os.path.exists(self._model_dir):
                self._pre_trained = True
                print_info(f"Loading model from localpath...{self._model_dir}")
                self._model = tf.keras.models.load_model(self._model_dir)
            else:
                self._model = self.define_model()

            self._hdfs_fs = None
            self._is_local_dir = True

    def load(self):
        self.load_tokenizer()
        self.load_model()

    @staticmethod
    def load_parquet_data(train_file_path, test_file_path, dev_file_path):
        train_file_path, test_file_path, dev_file_path = os.path.expanduser(train_file_path), \
                                                         os.path.expanduser(test_file_path), \
                                                         os.path.expanduser(dev_file_path)
        return pd.read_parquet(train_file_path, engine="fastparquet"), \
               pd.read_parquet(test_file_path, engine="fastparquet"), \
               pd.read_parquet(dev_file_path, engine="fastparquet")

    def export_tf_model(self, model, export_path):
        tf.keras.models.save_model(
            model,
            export_path,
            overwrite=False,
            include_optimizer=True,
            save_format=None,
            #signatures=None,
            #options=None
        )

    def save(self):
        if self._is_local_dir:
            if os.path.exists(self._model_dir):
                print_info("Model exists")
            print_info(f"Saving model to {self._model_dir}")
            check_n_mk_dirs(self._model_dir, is_remove=self._wipe_old_data)
            self._model.save(os.path.join(self._model_dir,'model.h5'), overwrite=False)
            with open(os.path.join(self._model_dir,'tokenizer.pickle'), 'wb') as handle:
                pickle.dump(self._tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            if self._hdfs_fs.exists(self._model_dir):
                return

            print_info(f"Saving model to {self._model_dir}")
            self._model.save(self._model_dir)
            with self._hdfs_fs.open(self._model_dir + 'tokenizer.pickle', 'wb') as handle:
                pickle.dump(self._tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

        # check_n_mk_dirs(self._model_export_dir.replace("//", "/"), is_remove=self._wipe_old_data)
        self.export_tf_model(model=self._model, export_path=os.path.join(self._model_export_dir.replace("//", "/")))

