import argparse
import gin
from tweepy.auth import OAuthHandler
from tweepy.streaming import Stream
from tweepy.streaming import StreamListener

# import socket
from kafka import KafkaProducer

from ssp.snorkel.ai_key_words import AIKeyWords
from ssp.logger.pretty_print import print_error, print_info

# http://docs.tweepy.org/en/latest/streaming_how_to.html
# we create this class that inherits from the StreamListener in tweepy StreamListener
from ssp.utils.eda import get_stop_words


class TweetsListener(StreamListener):
    def __init__(self, kafka_addr='localhost:9092', topic='twitter_data'):
        StreamListener.__init__(self)
        # Kafka settings
        self._kafka_producer = KafkaProducer(bootstrap_servers=kafka_addr)
        self._kafka_topic = topic

    def on_data(self, data):
        print_info(data)
        self._kafka_producer.send(self._kafka_topic, data.encode('utf-8')).get(timeout=10)
        return True

    def if_error(self, status):
        print(status)
        return True

@gin.configurable
class TwitterProducer(object):
    """
    Twitter ingestion class
    - Gets the twitter stream data and dumps the data into Kafka topic
    - Starts the Spark Structured Streaming against the Kafka topic and dumps the data to HDFS
    """
    def __init__(self,
                 twitter_consumer_key=None,
                 twitter_consumer_secret=None,
                 twitter_access_token=None,
                 twitter_access_secret=None,
                 mode=False,
                 kafka_address='localhost:9092',
                 kafka_topic='twitter_data',
                 filter_words=AIKeyWords.ALL_FP.split("|")):
        self._twitter_consumer_key = twitter_consumer_key
        self._twitter_consumer_secret = twitter_consumer_secret
        self._twitter_access_token = twitter_access_token
        self._twitter_access_secret = twitter_access_secret

        self._kafka_addr = kafka_address
        self._kafka_topic = kafka_topic

        self._filter_words = filter_words

        self._mode = mode

    def twitter_kafka_stream(self):
        auth = OAuthHandler(self._twitter_consumer_key, self._twitter_consumer_secret)
        auth.set_access_token(self._twitter_access_token, self._twitter_access_secret)

        twitter_stream = Stream(auth, TweetsListener(kafka_addr=self._kafka_addr, topic=self._kafka_topic))
        # https://developer.twitter.com/en/docs/tweets/filter-realtime/api-reference/post-statuses-filter
        # https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
        if self._mode == "ai_stopwords":
            if len(self._filter_words) < 400:
                count = 400 - len(self._filter_words)
                stop_words = get_stop_words()[:count]
                track = self._filter_words + stop_words
        elif self._mode == "stopwords":
            track = get_stop_words()[6:-20]
        else:
            track = self._filter_words
        twitter_stream.filter(track=track, languages=["en"])


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
