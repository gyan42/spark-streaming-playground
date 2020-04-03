import argparse
import gin
from pyspark.sql import SparkSession

from ssp.spark.streaming.analytics.sentiment_analysis import SentimentAnalysis

if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark SentimentAnalysis pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config/default_ssp_config.gin",
                          required=False,
                          help="File path of config.ini")

    parsed_args = optparse.parse_args()

    gin.parse_config_file(parsed_args.config_file)

    nlp_processing = SentimentAnalysis()

    nlp_processing.process()
