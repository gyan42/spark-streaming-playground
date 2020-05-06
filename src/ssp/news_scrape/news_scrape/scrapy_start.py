'''
Created on 09-Apr-2020

@author: srinivasan
'''
from twisted.internet.defer import Deferred
from scrapy.cmdline import execute
from builtins import SystemExit


def execute_call(spider_name):
    try:
        execute(['scrapy', 'crawl', spider_name])
    except SystemExit:
        pass
    return spider_name


def show(spider_name):
    print("===========================> completed" , spider_name)


d = Deferred()

d.addCallback(execute_call)
d.addCallback(show)
d.callback('timesofindia')
print("=======final")
