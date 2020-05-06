#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

from pyspark.sql import SparkSession


class StreamerBase(object):
    """
    Good read on Spark Streaming: https://www.slideshare.net/databricks/deep-dive-into-stateful-stream-processing-in-structured-streaming-with-tathagata-das

    When it comes to describing the semantics of a delivery mechanism, there are three basic categories:

    at-most-once delivery means that for each message handed to the mechanism, that message is delivered once or not at all; in more casual terms it means that messages may be lost.
    at-least-once delivery means that for each message handed to the mechanism potentially multiple attempts are made at delivering it, such that at least one succeeds; again, in more casual terms this means that messages may be duplicated but not lost.
    exactly-once delivery means that for each message handed to the mechanism exactly one delivery is made to the recipient; the message can neither be lost nor duplicated.

    The first one is the cheapest—highest performance, least implementation overhead—because it can be done in a fire-and-forget fashion without keeping state at the sending end or in the transport mechanism. The second one requires retries to counter transport losses, which means keeping state at the sending end and having an acknowledgement mechanism at the receiving end. The third is most expensive—and has consequently worst performance—because in addition to the second it requires state to be kept at the receiving end in order to filter out duplicate deliveries.

    """

    def __init__(self,
                 spark_master,
                 checkpoint_dir,
                 warehouse_location,
                 kafka_bootstrap_servers,
                 kafka_topic,
                 processing_time='5 seconds'):
        self._spark_master = spark_master
        self._checkpoint_dir = checkpoint_dir
        self._warehouse_location = warehouse_location
        self._kafka_bootstrap_servers = kafka_bootstrap_servers
        self._kafka_topic = kafka_topic
        self._processing_time = processing_time
        self._spark = None
    
    @property
    def sparkSession(self):
        return self._get_spark()

    def _get_spark(self):
        """
        :return:Spark Session
        """
        if not self._spark:
            self._spark = SparkSession.builder. \
                appName("TwitterRawDataIngestion"). \
                master(self._spark_master). \
                config("spark.sql.streaming.checkpointLocation", self._checkpoint_dir). \
                config("spark.sql.warehouse.dir", self._warehouse_location). \
                enableHiveSupport(). \
                getOrCreate()
            self._spark.sparkContext.setLogLevel("ERROR")
            self._spark.conf.set("spark.sql.streaming.metricsEnabled", "true")
        return self._spark

    def _get_source_stream(self, kafka_topic):
        raise NotImplementedError

    @staticmethod
    def _get_schema():
        raise NotImplementedError

    def visualize(self):
        """
        For debugging purporse
        :return:
        """

        sdf = self._get_source_stream(self._kafka_topic)

        def foreach_batch_function(df, epoch_id):
            # Transform and write batchDF
            df.show(50, True)

        sdf.writeStream.foreachBatch(foreach_batch_function).start().awaitTermination()

    def structured_streaming_dump(self, path, termination_time=None):
        # dump the data into bronze lake path
        sdf = self._get_source_stream(self._kafka_topic)

        sdf.writeStream. \
            format("parquet"). \
            outputMode("append"). \
            option("path", path). \
            option("checkpointLocation", self._checkpoint_dir). \
            trigger(processingTime=self._processing_time). \
            start().awaitTermination(termination_time)
