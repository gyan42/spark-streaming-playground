import re
import gin
import json
import threading

from tweepy.auth import OAuthHandler
from tweepy.streaming import Stream
from tweepy.streaming import StreamListener

# import socket
from kafka import KafkaProducer

from ssp.utils.ai_key_words import AIKeyWords
from ssp.logger.pretty_print import print_error, print_info

# http://docs.tweepy.org/en/latest/streaming_how_to.html
# we create this class that inherits from the StreamListener in tweepy StreamListener
from ssp.utils.eda import get_stop_words


def pick_text(text, rtext, etext):
    ret = ""
    if etext:
        ret = etext
    elif rtext:
        ret = rtext
    elif text:
        ret = text
    else:
        ret = ""

    return re.sub("\n|\r", "", ret).strip()


class TweetsListener(StreamListener):

    def __init__(self,
                 kafka_addr='localhost:9092',
                 topic='ai_tweets_topic',
                 is_ai=False):
        StreamListener.__init__(self)
        # Kafka settings
        self._kafka_producer = KafkaProducer(bootstrap_servers=kafka_addr)
        self._kafka_topic = topic
        self._is_ai = is_ai

    def on_data(self, data):
        data_dict = json.loads(data)

        if "text" in data_dict.keys():
            text = data_dict["text"]
        else:
            text = None

        if "extended_tweet" in data_dict.keys():
            etext = data_dict["extended_tweet"]["full_text"]
        else:
            etext = None

        if "retweeted_status" in data_dict.keys():
            if "extended_tweet" in data_dict["retweeted_status"].keys():
                rtext = data_dict["retweeted_status"]["extended_tweet"]["full_text"]
            else:
                rtext = None
        else:
            rtext = None

        text = pick_text(text=text, rtext=rtext, etext=etext)

        if self._is_ai:
            print_info(text)
        else:
            print_error(text)
        # with open("/tmp/tweets/{}.json".format(json.loads(data)["id_str"]), "wt", encoding='utf-8') as file:
        #     file.write(data)
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
                 kafka_topic_1='ai_tweets_topic',
                 kafka_topic_2='mix_tweets_topic',
                 topic_2_filter_words=None):
        self._twitter_consumer_key = twitter_consumer_key
        self._twitter_consumer_secret = twitter_consumer_secret
        self._twitter_access_token = twitter_access_token
        self._twitter_access_secret = twitter_access_secret

        self._kafka_addr = kafka_address
        self._kafka_topic_1 = kafka_topic_1
        self._kafka_topic_2 = kafka_topic_2

        self._topic_2_filter_words = topic_2_filter_words

        self._mode = mode

    def twitter_kafka_stream(self, kafka_topic, keywords, is_ai=False):
        """

        :param kafka_topic:
        :param keywords:
        :param is_ai:
        :return:
        """
        auth = OAuthHandler(self._twitter_consumer_key, self._twitter_consumer_secret)
        auth.set_access_token(self._twitter_access_token, self._twitter_access_secret)

        print_info("\n\n---------------------------------------------------------------------------------\n\n")
        print_info(f"Kafka topic : {kafka_topic} Twitter Keywords : {keywords}")
        print_info("\n\n---------------------------------------------------------------------------------\n\n")
        
        while True:
            try:
                twitter_stream = Stream(auth, TweetsListener(kafka_addr=self._kafka_addr, topic=kafka_topic, is_ai=is_ai))
                # https://developer.twitter.com/en/docs/tweets/filter-realtime/api-reference/post-statuses-filter
                # https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
                twitter_stream.filter(track=keywords, languages=["en"])
            except Exception as e:
                print("Error: Restarting the twitter stream")

    def run(self):
        """
        Starts two Kafka producers
        :return:
        """
        if self._topic_2_filter_words is None:
            self._topic_2_filter_words = AIKeyWords.ALL.split("|")

        ai_stream = threading.Thread(target=self.twitter_kafka_stream, args=(self._kafka_topic_1, AIKeyWords.POSITIVE.split("|"), True,))
        non_ai_stream = threading.Thread(target=self.twitter_kafka_stream, args=(self._kafka_topic_2, self._topic_2_filter_words,))

        ai_stream.setDaemon(True)
        non_ai_stream.setDaemon(True)
        ai_stream.start()
        non_ai_stream.start()

        ai_stream.join()
        non_ai_stream.join()


