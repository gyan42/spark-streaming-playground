#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

import configparser
import os
from configparser import ExtendedInterpolation, NoOptionError
from ssp.logger.pretty_print import *


class ConfigManager(object):
    """
    Config manager to read ini file
    """
    def __init__(self, config_path=None, key_value_pair_dict=None, string=None):
        """
        Initializes the configmanager using configparser
        :param config_path: File path
        :param key_value_pair_dict: Python dict
        :param string: Plain string in acceptable format
        """
        # set the path to the _config file
        self.config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
        self.config_path = config_path
        self.key_value_pair_dict = key_value_pair_dict
        self.string = string

        if self.config_path is not None:
            print_info("Reading _config from : " + config_path)
            if not os.path.exists(self.config_path):
                raise RuntimeError("{} file not found".format(self.config_path))
            self.config.read(self.config_path)
        elif self.key_value_pair_dict is not None:
            print_info("Reading _config from dict")
            self.config.read_dict(dictionary=self.key_value_pair_dict)
        elif self.string is not None:
            print_info("Reading _config from string")
            self.config.read_string(string=string)
        else:
            raise AssertionError("Either config file path or Key Value string should be given")

    def items(self, section, raw=False, vars=None):
        self.config.items(section=section, raw=raw, vars=vars)

    def get_sections(self):
        return self.config._sections.keys()

    def set_item(self, section, option, value):
        self.config.set(section=section,
                        option=option,
                        value=value)

    def get_item(self, section, option) -> str:
        try:
            return self.config.get(section=section,
                                   option=option)
        except NoOptionError:
            print_error("{} -> {} not found in {}".format(section, option, self.config_path))
            return None

    def add_section(self, section):
        self.config.add_section(section)

    def get_item_as_float(self, section, option):
        """
        Returns the value as float
        :param section:
        :param option:
        :return:
        """
        return self.config.getfloat(section=section,
                                    option=option)

    def get_item_as_int(self, section, option):
        """
        Returns the value as int
        :param section:
        :param option:
        :return:
        """
        return self.config.getint(section=section,
                                  option=option)

    def get_item_as_boolean(self, section, option):
        """
        Returns the value as bool
        :param section:
        :param option:
        :return:
        """
        return self.config.getboolean(section=section,
                                      option=option)

    def save_config(self):
        # Writing our configuration file to '_config'
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
