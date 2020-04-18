#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import argparse
import gin

# import socket

from ssp.kafka.producer import TwitterProducer

# http://docs.tweepy.org/en/latest/streaming_how_to.html
# we create this class that inherits from the StreamListener in tweepy StreamListener

if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config/twitter_ssp_config.gin",
                          required=False,
                          help="File path of gin config file")

    optparse.add_argument("-sw", "--mode",
                          type=str,
                          default="both",
                          required=False,
                          help="[topic1, topic2, both]")

    parsed_args = optparse.parse_args()

    gin.parse_config_file(parsed_args.config_file)

    producer = TwitterProducer()
    producer.run(stream=parsed_args.mode)
