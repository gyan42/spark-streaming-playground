'''
Created on 04-May-2020

@author: srinivasan
'''
#!/usr/bin/env python
from pyspark.sql.types import StructType, StringType, ArrayType

from ssp.logger.pretty_print import print_info
from ssp.spark.streaming.common.streamer_base import StreamerBase
from pyspark.sql.functions import from_json, col
from pyspark.sql.dataframe import DataFrame
import gin


class ScrapyStreamBase(StreamerBase):
    
    def _get_source_stream(self, kafka_topic=None) -> DataFrame:
        if kafka_topic:
            self._kafka_topic = kafka_topic

        print_info("\n\n------------------------------------------------------------------------------------------\n\n")
        print_info(f"\t\t\t Kafka topis is {self._kafka_topic}")
        print_info("\n\n------------------------------------------------------------------------------------------\n\n")
        
        spark = self._get_spark()
        
        df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self._kafka_bootstrap_servers) \
            .option("subscribe", self._kafka_topic) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()
            
        return df.selectExpr("cast (value as STRING)")\
         .select(from_json("value", self._get_schema()).alias("news_data")).select(col('news_data.*'))
    
    @staticmethod
    def _get_schema():
        return StructType(). \
            add('headline', StringType(), False).add('synopsis', StringType(), False).\
            add('link', StringType(), False).add('authors', ArrayType(StringType()), False).\
            add('published_date', StringType(), False).add('place', StringType(), False).\
            add('domain', StringType(), False).add('section', StringType(), False).\
            add('content', StringType(), False).add('tags', ArrayType(StringType()), False)


@gin.configurable
class Scrapy_Data_Stream_Consumer(ScrapyStreamBase):
    
    def __init__(self,
                 spark_master,
                 checkpoint_dir,
                 warehouse_location,
                 kafka_bootstrap_servers,
                 kafka_topic,
                 bronze_parquet_dir,
                 processing_time='5 seconds'):
        super().__init__(spark_master, checkpoint_dir, warehouse_location,
                 kafka_bootstrap_servers, kafka_topic, processing_time)
        self._bronze_parquet_dir = bronze_parquet_dir
    
    def dump_to_Hdfs(self):
        self.structured_streaming_dump(self._bronze_parquet_dir)
    
