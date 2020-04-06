import argparse
import gin
import os
import json
import requests

from ssp.logger.pretty_print import print_info, print_error
from ssp.dl.classifier.naive_text_classifier import NaiveTextClassifier

# https://towardsdatascience.com/tensorflow-2-0-data-transformation-for-text-classification-b86ee2ad8877
if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config/twitter_ssp_config.gin",
                          required=False,
                          help="File path of config.ini")

    opt = optparse.parse_args()
    gin.parse_config_file(opt.config_file)

    classifer = NaiveTextClassifier()
    classifer.load()
    classifer.preprocess_train_data()
    classifer.train()
    classifer.evaluate()
    classifer.save()

    print_info(classifer.predict(classifer._test_df["text"].values)[:10])

