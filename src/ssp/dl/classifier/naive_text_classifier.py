import os

import gin
import pandas as pd
import tensorflow as tf
import spacy
import pickle

from ssp.logger.pretty_print import print_info, print_error
from ssp.utils.misc import check_n_mk_dirs


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
                 batch_size=64):
        self._pre_trained = False
        self._text_column = text_column
        self._label_column = label_column
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

        check_n_mk_dirs(model_dir, is_remove=wipe_old_data)
        self._model_dir = model_dir

        if os.path.exists(self._model_dir + 'tokenizer.pickle'):
            print_info(f"Loading tokenizer... {self._model_dir + 'tokenizer.pickle'}")
            with open(self._model_dir + 'tokenizer.pickle', 'rb') as f:
                self._tokenizer = pickle.load(f)
        else:
            self._tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=self._num_words, oov_token='<UNK>')

        self._model_name = "naive_text_classifier.h5"

        if os.path.exists(self._model_dir + self._model_name):
            self._pre_trained = True
            print_info(f"Loading model...{self._model_dir + self._model_name}")
            self._model = tf.keras.models.load_model(self._model_dir + self._model_name)
        else:
            self._model = self.get_model()

        self._train_seqs = None
        self._test_seqs = None

    @staticmethod
    def load_parquet_data(train_file_path, test_file_path, dev_file_path):
        return pd.read_parquet(train_file_path, engine="fastparquet"), \
               pd.read_parquet(test_file_path, engine="fastparquet"), \
               pd.read_parquet(dev_file_path, engine="fastparquet")


    def fit_tokenizer(self):
        # create tokenizer for our data
        self._tokenizer.fit_on_texts(self._train_df[self._text_column])

    def transform(self, text_list):
        # convert text data to numerical indexes
        seqs = self._tokenizer.texts_to_sequences(text_list)
        # pad data up to SEQ_LEN (note that we truncate if there are more than SEQ_LEN tokens)
        seqs = tf.keras.preprocessing.sequence.pad_sequences(seqs, maxlen=self._seq_len, padding="post")
        return seqs

    def preprocess_text(self):
        self.fit_tokenizer()
        self._train_seqs = self.transform(text_list=self._train_df[self._text_column])
        self._test_seqs = self.transform(text_list=self._test_df[self._text_column])

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
        self._model.save(self._model_dir + self._model_name)
        # saving
        with open(self._model_dir + 'tokenizer.pickle', 'wb') as handle:
            pickle.dump(self._tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def predict(self, text_list):
        seqs = self.transform(text_list=text_list)
        preds = self._model.predict(seqs)
        return preds