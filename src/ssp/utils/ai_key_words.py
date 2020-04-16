#!/usr/bin/env python

__author__ = "Mageswaran Dhandapani"
__copyright__ = "Copyright 2020, The Spark Structured Playground Project"
__credits__ = []
__license__ = "Apache License"
__version__ = "2.0"
__maintainer__ = "Mageswaran Dhandapani"
__email__ = "mageswaran1989@gmail.com"
__status__ = "Education Purpose"

class AIKeyWords(object):
    AI = "#AI|Artificial Intelligence|robotics"
    ML = "machinelearningengineer|Machine Learning|scikit|#ML|mathematics"
    DL = "DeepLearning|Deep Learning|#DL|Tensorflow|Pytorch|Neural Network|NeuralNetwork"
    CV = "computervision|computer vision|machine vision|machinevision|convolutional network|convnet|image processing"
    NLP = "NLP|naturallanguageprocessing|natural language processing|text processing|text analytics|nltk|spacy"
    DATA = "iot|datasets|dataengineer|analytics|bigdata|big data|data science|data analytics|data insights|data mining|distributed computing|parallel processing|apache spark|hadoop|apache hive|airflow|mlflow|apache kafka|hdfs|apache|kafka"
    TWEET_HASH_TAGS = "dataanalysis|AugmentedIntelligence|datascience|machinelearning|rnd|businessintelligence|DigitalTransformation|datamanagement|ArtificialIntelligence"
    FALSE_POSITIVE = "gpu|nvidia|maths|mathematics|intelligence|conspiracy|astrology|vedic|tamil|text|computer|ebook|pdf|learning|big|insights|processing|network|machine|artifical|data|science|parallel|computing|deep|vision|natural|language|data"
    RANDOM_TOPICS = "nature|climate|space|earth|animals|plants|astrology|horoscope|occult|hidden science|conspiracy|hinduism|hindu|vedic"

    POSITIVE = AI + "|" + ML + "|" + DL + "|" + CV + "|" + NLP + "|" + DATA + "|" + TWEET_HASH_TAGS
    ALL = POSITIVE + "|" + FALSE_POSITIVE + "|" + RANDOM_TOPICS