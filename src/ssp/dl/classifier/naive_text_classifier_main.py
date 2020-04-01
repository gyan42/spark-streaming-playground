import argparse
import gin
import os

from ssp.logger.pretty_print import print_info, print_error
from ssp.dl.classifier.naive_text_classifier import NaiveTextClassifier

# https://towardsdatascience.com/tensorflow-2-0-data-transformation-for-text-classification-b86ee2ad8877
if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config/twitter_ssp_config.gin",
                          required=False,
                          help="File path of config.ini")

    optparse.add_argument("-tp", "--train_file_path",
                          default=f"{os.path.expanduser('~')}/ssp/data/dump/raw_tweet_dataset_0/train.parquet",
                          required=False,
                          help="Train parquet file path")

    optparse.add_argument("-ttp", "--test_file_path",
                          default=f"{os.path.expanduser('~')}/ssp/data/dump/raw_tweet_dataset_0/test.parquet",
                          required=False,
                          help="Test parquet file path")

    optparse.add_argument("-dp", "--dev_file_path",
                          default=f"{os.path.expanduser('~')}/ssp/data/dump/raw_tweet_dataset_0/dev.parquet",
                          required=False,
                          help="Dev parquet file path")

    optparse.add_argument("-md", "--model_dir",
                          default=f"{os.path.expanduser('~')}/ssp/model/raw_tweet_dataset_0/",
                          required=False,
                          help="Dev parquet file path")

    opt = optparse.parse_args()
    gin.parse_config_file(opt.config_file)

    train_df, test_df, dev_df = NaiveTextClassifier.load_parquet_data(train_file_path=opt.train_file_path,
                                                                      test_file_path=opt.test_file_path,
                                                                      dev_file_path=opt.dev_file_path)

    classifer = NaiveTextClassifier(train_df_or_path=train_df,
                                    test_df_or_path=test_df,
                                    dev_df_or_path=dev_df,
                                    model_dir=opt.model_dir)
    classifer.preprocess_text()
    classifer.train()
    classifer.evaluate()
    classifer.save_model()

    print_info(classifer.predict(test_df["text"].values))