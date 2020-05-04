#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import sys
import logging
from ssp.utils.singleton_metaclass import Singleton

def str_to_level(log_level):
    if log_level == "error":
        return logging.ERROR
    elif log_level == "debug":
        return logging.DEBUG
    elif log_level == "info":
        return logging.INFO
    else:
        return logging.ERROR


class PythonLogger(metaclass=Singleton):
    def __init__(self, log_level: str):
        self.logger = logging.getLogger()
        self.logger.setLevel(str_to_level(log_level))

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(str_to_level(log_level))
        formatter = logging.Formatter('>>>>>>>> %(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        logging.basicConfig(filename="./log.txt",
                            filemode='a',
                            format=formatter,
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

    def info(self, info):
        self.logger.info(str(info))

    def error(self, info):
        self.logger.error(str(info))

    def warn(self, info):
        self.logger.warning(str(info))

    def debug(self, info):
        self.logger.debug(str(info))
