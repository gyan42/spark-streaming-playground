#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import gin
import argparse
from ssp.ml.dataset import SSPMLDataset


if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config/default_ssp_config.gin",
                          required=False,
                          help="File path of config.ini")

    optparse.add_argument("-v", "--version",
                          default=0,
                          type=int,
                          required=True,
                          help="Version of raw tweet dump data to use ")

    optparse.add_argument("-m", "--mode",
                          default="split",
                          type=str,
                          required=False,
                          help="[split/download] Prepare the dataset by splitting raw data table "
                               "or downloads the annotated data from tables")
    parsed_args = optparse.parse_args()

    gin.parse_config_file(parsed_args.config_file)
    dataset = SSPMLDataset()

    if parsed_args.mode == "split":
        dataset.split_n_store(version=parsed_args.version)
    else:
        dataset.download_n_store(version=parsed_args.version)
