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
from ssp.logger.spark_logger import SparkLogger, Singleton
from ssp.logger.yagmail import YagMail
from ssp.logger.python_logger import PythonLogger
import logging
import inspect
from inspect import getframeinfo, stack


class SSPLogger(metaclass=Singleton):
    """
    Class that wraps all logging functionality.
    It supports following:
    - Spark logging, if sparksession is provided or it ognores it
    - Python way of logging into a file "log.txt"
    - Sends the email based on the user flag
    """

    def __init__(self,
                 app_name,
                 parsed_args,
                 pipeline_name="Default",
                 log_level="info",
                 sparksession=None):
        self._run_name = app_name
        self._pipeline_name = pipeline_name
        if parsed_args:
            self._config_dir = parsed_args.config_dir_path
        self._logger = SparkLogger(app_name=app_name, sparksession=sparksession)
        self._py_logger = PythonLogger(log_level=log_level)

    @staticmethod
    def add_script_details(message):
        caller = getframeinfo(stack()[1][0])
        return "%s:%d : %s" % (caller.filename, caller.lineno, message)

    def lineno(self):
        """Returns the current line number in your code"""
        return str(inspect.currentframe().f_back.f_lineno)

    def email(self, subject, contents, config_dir):
        subject = self._pipeline_name + " : " + subject
        YagMail.email_notifier_ini(subject=subject, contents=contents, config_dir=config_dir)

    def info(self, msg, subject="",  send_mail=False):
        text = str(subject) + " >>> " + str(msg)
        print_info(text)
        self._logger.info(text)
        self._py_logger.info(text)
        if send_mail:
            self.email(subject=subject, contents=msg, config_dir=self._config_dir)

    def debug(self, msg, subject="",  send_mail=False):
        text = str(subject) + " >>> " + str(msg)
        print_debug(text)
        self._logger.debug(text)
        self._py_logger.debug(text)
        if send_mail:
            self.email(subject=subject, contents=msg, config_dir=self._config_dir)

    def warning(self, msg, subject="",  send_mail=False):
        text = str(subject) + " >>> " + str(msg)
        print_warn(text)
        self._logger.warn(text)
        self._py_logger.warn(text)
        if send_mail:
            self.email(subject=subject, contents=msg, config_dir=self._config_dir)

    def error(self, msg, subject="",  send_mail=False):
        text = str(subject) + " >>> " + str(msg)
        print_error(text)
        self._logger.error(text)
        self._py_logger.error(text)
        if send_mail:
            self.email(subject=subject, contents=msg, config_dir=self._config_dir)
