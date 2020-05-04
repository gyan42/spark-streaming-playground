#!/usr/bin/env python

"""
SSP modules that handles all data at ingestion level from Twitter stream
"""

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import argparse
import gin
from ssp.spark.streaming.consumer.twiteer_stream_consumer import TwitterDataset



if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config/default_ssp_config.gin",
                          required=False,
                          help="File path of config.ini")

    optparse.add_argument("-m", "--mode",
                          required=True,
                          help="[dump_into_bronze_lake, visualize, local_dir_dump, dump_into_postgresql]")

    optparse.add_argument("-s", "--num_records",
                          required=False,
                          default=50000,
                          type=int,
                          help="Number of records to collect before shutting down")

    optparse.add_argument("-id", "--run_id",
                          required=False,
                          type=int,
                          help="Run ID")

    optparse.add_argument("-p", "--path",
                          required=False,
                          default="file:///tmp/ssp/raw_data/",
                          help="Path to store the records")

    parsed_args = optparse.parse_args()

    gin.parse_config_file(parsed_args.config_file)

    dataset = TwitterDataset()

    if parsed_args.mode == "dump_into_bronze_lake":
        dataset.dump_into_bronze_lake()
    elif parsed_args.mode == "visualize":
        dataset.visualize()
    elif parsed_args.mode == "local_dir_dump":
        dataset.structured_streaming_dump(path=parsed_args.path, termination_time=int(parsed_args.seconds))
    elif parsed_args.mode == "dump_into_postgresql":
        dataset.dump_into_postgresql(run_id=parsed_args.run_id, num_records=parsed_args.num_records)
    else:
        raise RuntimeError("Invalid choice")
