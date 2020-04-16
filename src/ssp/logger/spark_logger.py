#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

from ssp.logger.pretty_print import *
from ssp.utils.singleton_metaclass import Singleton


class SparkLogger(metaclass=Singleton):
    def __init__(self, app_name, sparksession = None):
        self._spark = sparksession
        self.log4jLogger = None

        if self._spark is not None:
            print_info("\n\n\nDigisightLogger is initialized with existing Spark Session\n\n\n")
            sparkContext =self._spark.sparkContext
            self.log4jLogger = sparkContext._jvm.org.apache.log4j

            #Return the fillmore log
            self.log4jLogger = self.log4jLogger.LogManager.getLogger(app_name)

    def info(self, info):
        if self.log4jLogger:
            self.log4jLogger.info(str(info))

    def error(self, info):
        if self.log4jLogger:
            self.log4jLogger.error(str(info))

    def warn(self, info):
        if self.log4jLogger:
            self.log4jLogger.warn(str(info))

    def debug(self, info):
        if self.log4jLogger:
            self.log4jLogger.debug(str(info))