import gin
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, col
from ssp.spark.udf.spacy_ner_udf import get_ner_udf


@gin.configurable
class SreamingTextClassifier(object):
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

        self._postgresql_host = postgresql_host
        self._postgresql_port = postgresql_port
        self._postgresql_database = postgresql_database
        self._postgresql_user = postgresql_user
        self._postgresql_password = postgresql_password

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