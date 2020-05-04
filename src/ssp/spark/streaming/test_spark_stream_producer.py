import os
from pytest_spark import spark_session

from ssp.spark.streaming.common.twitter_streamer_base import TwitterStreamerBase


def _get_test_spark_stream(spark_session):
    schema = TwitterStreamerBase._get_schema()
    test_files_path = "file:///" + os.path.abspath("data/streams/tweets/")
    sdf = spark_session.readStream.format("json").schema(schema).load(test_files_path)
    return sdf

def test_spark_stream(spark_session):
    sdf = _get_test_spark_stream(spark_session)
    count_acc = spark_session.sparkContext.accumulator(0)

    def foreach_batch_function(df, epoch_id, count_acc):
        # Transform and write batchDF
        count = df.count()

        count_acc += count

    sdf.writeStream.foreachBatch(lambda df, epoch_id :
                                 foreach_batch_function(df=df, epoch_id=epoch_id, count_acc=count_acc)).start().processAllAvailable()
    assert count_acc.value == 1000

