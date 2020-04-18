#!/usr/bin/env python

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
from ssp.snorkel.labelling_function import SSPLabelEvaluator

if __name__ == "__main__":
    optparse = argparse.ArgumentParser("Twitter Spark Text Processor pipeline:")

    optparse.add_argument("-cfg", "--config_file",
                          default="config/default_ssp_config.gin",
                          required=False,
                          help="File path of config.ini")

    optparse.add_argument("-v", "--version",
                          default=0,
                          required=False,
                          help="Version number. To be used to pick the respective tables for labeling")


    parsed_args = optparse.parse_args()

    gin.parse_config_file(parsed_args.config_file)
    dataset = SSPLabelEvaluator()
    dataset.run_labeler(version=parsed_args.version)
