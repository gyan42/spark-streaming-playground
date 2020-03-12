import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col
from ssp.customudf.spacy_ner_udf import get_ner_udf

from ssp.utils.configuration import StreamingConfigs


class NerExrtaction(StreamingConfigs):
    def __init__(self, config_file_path):
        StreamingConfigs.__init__(self, config_file_path=config_file_path)

        self.spark = SparkSession.builder. \
            appName("twitter_stream"). \
            master(self._spark_master). \
            config("spark.sql.streaming.checkpointLocation", self._checkpoint_dir). \
            getOrCreate()

        self.spark.sparkContext.setLogLevel("error")

    def process(self):
        userSchema = self.spark.read.parquet(self._bronze_parquet_dir).schema

        tweet_table_stream = self.spark.readStream. \
            schema(userSchema). \
            format("parquet"). \
            option("ignoreChanges", "true"). \
            load(self._bronze_parquet_dir)

        tweet_table_stream = tweet_table_stream. \
            withColumn("ner", explode(get_ner_udf(col("text"))))

        def foreach_batch_function(df, epoch_id):
            # Transform and write batchDF
            df.printSchema()
            df.select(["ner"]).show(50, False)

            mode = "overwrite"
            url = "jdbc:postgresql://{}:{}/{}".format(self._postgresql_host,
                                                      self._postgresql_port,
                                                      self._postgresql_database)
            properties = {"user": self._postgresql_user,
                          "password": self._postgresql_password,
                          "driver": "org.postgresql.Driver"}
            df.write.jdbc(url=url, table="ner", mode=mode, properties=properties)

        tweet_table_stream.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()


if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor NLP pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config.ini",
                          required=False,
                          help="File path of config.ini")

    parsed_args = optparse.parse_args()

    nlp_processing = NerExrtaction(config_file_path=parsed_args.config_file)

    nlp_processing.process()
