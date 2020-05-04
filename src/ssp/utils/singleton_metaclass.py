#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

from weakref import WeakValueDictionary

class Singleton(type):
    """
    References:
        - https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
        - https://stackoverflow.com/questions/100003/what-are-metaclasses-in-python
        - https://stackoverflow.com/questions/43619748/destroying-a-singleton-object-in-python
    """
    _instances = WeakValueDictionary()
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
