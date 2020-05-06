import socket
import gin
from ssp.spark.streaming.consumer.twiteer_stream_consumer import TwitterDataset
from ssp.spark.streaming.consumer.scrapy_stream_consumer import Scrapy_Data_Stream_Consumer


@gin.configurable
def get_local_spark_master():
    return "spark://" + socket.gethostname() + ":7077"
