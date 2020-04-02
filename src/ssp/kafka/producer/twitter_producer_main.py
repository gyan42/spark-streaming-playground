import argparse
import gin
from tweepy.auth import OAuthHandler
from tweepy.streaming import Stream
from tweepy.streaming import StreamListener

# import socket
from kafka import KafkaProducer

from ssp.kafka.producer import TwitterProducer
from ssp.snorkel.ai_key_words import AIKeyWords
from ssp.logger.pretty_print import print_error, print_info

# http://docs.tweepy.org/en/latest/streaming_how_to.html
# we create this class that inherits from the StreamListener in tweepy StreamListener
from ssp.utils.eda import get_stop_words

if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config/twitter_ssp_config.gin",
                          required=False,
                          help="File path of gin config file")

    optparse.add_argument("-sw", "--mode",
                          type=str,
                          default="ai",
                          required=False,
                          help="Filter twitter stream including one of [ai|stopwords|ai_stopwords] keywords")

    parsed_args = optparse.parse_args()

    gin.parse_config_file(parsed_args.config_file)

    producer = TwitterProducer(mode=parsed_args.mode)
    producer.twitter_kafka_stream()
