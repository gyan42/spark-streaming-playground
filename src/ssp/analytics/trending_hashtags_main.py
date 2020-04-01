import argparse
import gin
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, explode
from pyspark.sql.types import ArrayType, StringType

from ssp.utils.config_manager import ConfigManager
from ssp.utils.configuration import StreamingConfigs


def extract_hashtag(text):
    if text is not None:
        text = text.replace('\n', ' ').replace('\r', '')
        text = text.split(" ")
        text = [word for word in text if "#" in word]
        if len(text) == 0:
            text = ["no tags"]
    else:
        text = ["no tags"]
    return text

extract_hashtag_udf = udf(extract_hashtag, ArrayType(StringType()))

@gin.configurable
class TrendingHashTags(object):
    def __init__(self,
                 checkpoint_dir="hdfs://localhost:9000/tmp/ssp/data/lake/checkpoint/",
                 bronze_parquet_dir="hdfs://localhost:9000/tmp/ssp/data/lake/bronze/",
                 warehouse_location="/opt/spark-warehouse/",
                 spark_master="spark://IMCHLT276:7077",
                 postgresql_host="localhost",
                 postgresql_port="5432",
                 postgresql_database="sparkstreamingdb",
                 postgresql_user="sparkstreaming",
                 postgresql_password="sparkstreaming"):

        self._spark_master = spark_master

        self._checkpoint_dir = checkpoint_dir
        self._bronze_parquet_dir = bronze_parquet_dir
        self._warehouse_location = warehouse_location


        self.spark = SparkSession.builder. \
            appName("TrendingHashTags"). \
            config("spark.sql.warehouse.dir", self._warehouse_location). \
            master(self._spark_master). \
            config("spark.sql.streaming.checkpointLocation", self._checkpoint_dir). \
            enableHiveSupport(). \
            getOrCreate()

        self.spark.sparkContext.setLogLevel("error")

        self._postgresql_host = postgresql_host
        self._postgresql_port = postgresql_port
        self._postgresql_database = postgresql_database
        self._postgresql_user = postgresql_user
        self._postgresql_password = postgresql_password

    def process(self):
        userSchema = self.spark.read.parquet(self._bronze_parquet_dir).schema
        tweet_table_stream = self.spark.readStream. \
            schema(userSchema).\
            format("parquet"). \
            option("ignoreChanges", "true"). \
            option("failOnDataLoss", "false"). \
            load(self._bronze_parquet_dir)

        tweet_table_stream.printSchema()

        tweet_table_stream = tweet_table_stream. \
            withColumn("hashtag", explode(extract_hashtag_udf(col("text")))). \
            groupBy("hashtag").count().sort(col("count").desc())

        def foreach_batch_function(df, epoch_id):
            # Transform and write batchDF
            df.printSchema()
            df.show(50, False)

            # TODO closure in effect, consider refactoring
            mode = "overwrite"
            url = "jdbc:postgresql://{}:{}/{}".format(self._postgresql_host,
                                                      self._postgresql_port,
                                                      self._postgresql_database)
            properties = {"user": self._postgresql_user,
                          "password": self._postgresql_password,
                          "driver": "org.postgresql.Driver"}
            # url = "jdbc:postgresql://localhost:5432/sparkstreamingdb"
            # properties = {"user": "sparkstreaming", "password": "sparkstreaming", "driver": "org.postgresql.Driver"}
            df.write.jdbc(url=url, table="trending_hashtags", mode=mode, properties=properties)


        tweet_table_stream.writeStream.outputMode("complete").foreachBatch(foreach_batch_function).start().awaitTermination()


if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config.ini",
                          required=False,
                          help="File path of config.ini")

    parsed_args = optparse.parse_args()

    gin.parse_config_file(parsed_args.config_file)

    nlp_processing = TrendingHashTags()

    nlp_processing.process()
