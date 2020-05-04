#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

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

def pick_text(text, rtext, etext):
    """
    Twitter Json data has three level of text. This function picks what is available in the order etext > rtext > text
    :param text: Plain text at top level of the Json with stipped content and an URL
    :param rtext: Retweeted full text
    :param etext: Extended retweeted full text
    :return:
    """
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
    """
    Tweepy StreamListener.
    Reference: http://docs.tweepy.org/en/latest/streaming_how_to.html
    
    :param kafka_addr: (str) Kafka host address <host_url:port>
    :param topic: (str) Kafka topic
    :param is_ai: (bool) Used to differentiate AI tweets wuth green color and red for other category tweets
    """
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
        """
        Gets triggered by the Twitter stream API
        :param data: Tweet Json data
        :return: dumps the data into Kafka topic
        """
        data_dict = json.loads(data)

        # Debug info
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

        # this is where the data is dumped into the Kafka topic
        self._kafka_producer.send(self._kafka_topic, data.encode('utf-8')).get(timeout=10)
        return True

    def if_error(self, status):
        print(status)
        return True


@gin.configurable
class TwitterProducer(object):
    """
    Twitter data ingestion. Gets the twitter stream data and dumps the data into Kafka topic(s).

    :param twitter_consumer_key: (str) Twitter Consumer Key
    :param twitter_consumer_secret: (str) Twitter Consumer secret
    :param twitter_access_token: (str)  Twitter Access token
    :param twitter_access_secret: (str) Twitter Access secret
    :param kafka_address: (str) Kafka host address <host_url:port>
    :param kafka_topic_1: (str) Tweet stream Kafka topic defaults to use  :func:`~ssp.utils.AIKeyWords.POSITIVE`
    :param kafka_topic_2: (str) Tweet stream Kafka topic
    :param topic_2_filter_words: (list) Filter words to be used for second stream
    """

    def __init__(self,
                 twitter_consumer_key=None,
                 twitter_consumer_secret=None,
                 twitter_access_token=None,
                 twitter_access_secret=None,
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

    def _twitter_kafka_stream(self, kafka_topic, keywords, is_ai=False):
        """

        :param kafka_topic:
        :param keywords:
        :param is_ai:
        :return:
        """
        auth = OAuthHandler(self._twitter_consumer_key, self._twitter_consumer_secret)
        auth.set_access_token(self._twitter_access_token, self._twitter_access_secret)

        print_info("\n\n---------------------------------------------------------------------------------\n\n")
        print_info(f"Kafka topic : {kafka_topic}")
        print_info(f"Twitter Keywords : {keywords}")
        print_info("\n\n---------------------------------------------------------------------------------\n\n")
        
        while True:
            try:
                twitter_stream = Stream(auth, TweetsListener(kafka_addr=self._kafka_addr, topic=kafka_topic, is_ai=is_ai))
                # https://developer.twitter.com/en/docs/tweets/filter-realtime/api-reference/post-statuses-filter
                # https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
                twitter_stream.filter(track=keywords, languages=["en"])
            except Exception as e:
                print("Error: Restarting the twitter stream")

    def run(self, stream="both"):
        """
        Starts two Kafka producers
        :return: None
        """
        if self._topic_2_filter_words is None:
            self._topic_2_filter_words = AIKeyWords.ALL.split("|")

        if stream == "topic1":
            ai_stream = threading.Thread(target=self._twitter_kafka_stream, args=(self._kafka_topic_1, AIKeyWords.POSITIVE.split("|"), True,))
            ai_stream.setDaemon(True)
            ai_stream.start()
            ai_stream.join()
        elif stream == "topic2":
            non_ai_stream = threading.Thread(target=self._twitter_kafka_stream,
                                             args=(self._kafka_topic_2, self._topic_2_filter_words,))

            non_ai_stream.setDaemon(True)
            non_ai_stream.start()
            non_ai_stream.join()
        else:
            ai_stream = threading.Thread(target=self._twitter_kafka_stream,
                                         args=(self._kafka_topic_1, AIKeyWords.POSITIVE.split("|"), True,))
            non_ai_stream = threading.Thread(target=self._twitter_kafka_stream,
                                             args=(self._kafka_topic_2, self._topic_2_filter_words,))

            ai_stream.setDaemon(True)
            non_ai_stream.setDaemon(True)
            ai_stream.start()
            non_ai_stream.start()

            ai_stream.join()
            non_ai_stream.join()





