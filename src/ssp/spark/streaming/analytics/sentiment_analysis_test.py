import pytest

from ssp.logger.pretty_print import print_error
from ssp.spark.streaming.analytics import SentimentAnalysis

def test_sentiment_analysis_members():
    for item in ['get_schema', 'get_source_stream', 'get_spark', 'hdfs_process',
                 'online_process', 'process', 'structured_streaming_dump', 'visualize']:
        assert item in dir(SentimentAnalysis)

