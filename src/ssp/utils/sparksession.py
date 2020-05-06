# from pyspark.sql import SparkSession
#
# def get_spark_session(config):
#     SparkSession.builder. \
#         appName("twitter_stream"). \
#         master(self._spark_master). \
#         config("spark.sql.warehouse.dir", warehouseLocation). \
#         config("spark.sql.streaming.checkpointLocation", self._checkpoint_dir). \
#         getOrCreate()
#
#
