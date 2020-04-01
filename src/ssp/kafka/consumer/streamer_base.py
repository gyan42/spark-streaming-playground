from pyspark.sql import SparkSession


class StreamerBase(object):
    def __init__(self, spark_master, checkpoint_dir, warehouse_location, processing_time):
        self._spark_master = spark_master
        self._checkpoint_dir = checkpoint_dir
        self._warehouse_location = warehouse_location
        self._processing_time = processing_time

    def get_spark(self):
        """
        :return:Spark Session
        """
        spark = SparkSession.builder. \
            appName("TwitterRawDataIngestion"). \
            master(self._spark_master). \
            config("spark.sql.streaming.checkpointLocation", self._checkpoint_dir). \
            config("spark.sql.warehouse.dir", self._warehouse_location). \
            enableHiveSupport(). \
            getOrCreate()
        spark.sparkContext.setLogLevel("ERROR")

        return spark

    def get_source_stream(self):
        raise NotImplementedError

    def get_schema(self):
        raise NotImplementedError

    def visualize(self):
        """
        For debugging purporse
        :return:
        """

        sdf = self.get_source_stream()

        def foreach_batch_function(df, epoch_id):
            # Transform and write batchDF
            df.show(50, True)

        sdf.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()

    def structured_streaming_dump(self, path, termination_time=None):
        # dump the data into bronze lake path
        sdf = self.get_source_stream()

        storeDF = sdf.writeStream. \
            format("parquet"). \
            outputMode("append"). \
            option("path", path). \
            option("checkpointLocation", self._checkpoint_dir). \
            trigger(processingTime=self._processing_time). \
            start().awaitTermination(termination_time)
