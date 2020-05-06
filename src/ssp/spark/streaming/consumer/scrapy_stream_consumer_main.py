'''
Created on 04-May-2020

@author: srinivasan
'''
#!/usr/bin/env python
import argparse
import gin
from ssp.spark.streaming.consumer.scrapy_stream_consumer import Scrapy_Data_Stream_Consumer

if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config/scrapy_config.gin",
                          required=False,
                          help="File path of config.ini")

    parsed_args = optparse.parse_args()

    gin.parse_config_file(parsed_args.config_file)

    consumer = Scrapy_Data_Stream_Consumer()
    consumer.dump_to_Hdfs()
