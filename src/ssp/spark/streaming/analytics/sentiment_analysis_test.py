#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

from ssp.spark.streaming.analytics import SentimentAnalysis


def test_sentiment_analysis_members():
    for item in ['_get_schema', '_get_source_stream', '_get_spark', '_hdfs_process',
                 '_online_process', 'process', 'structured_streaming_dump', 'visualize']:
        assert item in dir(SentimentAnalysis)

