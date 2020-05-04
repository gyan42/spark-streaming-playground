#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"


CBOLD     = '\33[1m'
CITALIC   = '\33[3m'
CURL      = '\33[4m'
CBLINK    = '\33[5m'
CBLINK2   = '\33[6m'
CSELECTED = '\33[7m'

CBLACK  = '\33[30m'

CGREEN  = '\33[32m'
CYELLOW = '\33[33m'

CVIOLET = '\33[35m'
CBEIGE  = '\33[36m'
CWHITE  = '\33[37m'

CBLACKBG  = '\33[40m'
CREDBG    = '\33[41m'
CGREENBG  = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG   = '\33[44m'
CVIOLETBG = '\33[45m'
CBEIGEBG  = '\33[46m'
CWHITEBG  = '\33[47m'

CGREY    = '\33[90m'
CRED2    = '\33[91m'


CBLUE2   = '\33[94m'
CVIOLET2 = '\33[95m'
CBEIGE2  = '\33[96m'
CWHITE2  = '\33[97m'

CGREYBG    = '\33[100m'
CREDBG2    = '\33[101m'
CGREENBG2  = '\33[102m'
CYELLOWBG2 = '\33[103m'
CBLUEBG2   = '\33[104m'
CVIOLETBG2 = '\33[105m'
CBEIGEBG2  = '\33[106m'
CWHITEBG2  = '\33[107m'

CEND      = '\33[0m'
CBLUE   = '\33[34m'
CYELLOW2 = '\33[93m'
CRED    = '\33[31m'
CGREEN2  = '\33[92m'

def print_info(*args):
    """
    Prints the string in green color
    :param args: user string information
    :return: stdout
    """
    print(CGREEN2 + str(*args) + CEND)

def print_error(*args):
    """
    Prints the string in red color
    :param args: user string information
    :return: stdout
    """
    print(CRED + str(*args) + CEND)

def print_warn(*args):
    """
    Prints the string in yellow color
    :param args: user string information
    :return: stdout
    """
    print(CYELLOW2 + str(*args) + CEND)

def print_debug(*args):
    """
    Prints the string in blue color
    :param args: user string information
    :return: stdout
    """
    print(CBLUE + str(*args) + CEND)