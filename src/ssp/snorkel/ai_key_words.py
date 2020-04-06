
class AIKeyWords(object):
    AI = "#AI|Artificial Intelligence|robotics"
    ML = "machinelearningengineer|Machine Learning|scikit|mathematics|#ML|maths"
    DL = "DeepLearning|Deep Learning|#DL|Tensorflow|Pytorch|Neural Network|NeuralNetwork|gpu|nvidia"
    CV = "computervision|computer vision|machine vision|machinevision|convolutional network|convnet|image processing"
    NLP = "NLP|naturallanguageprocessing|natural language processing|text processing|text analytics|nltk|spacy"
    DATA = "dataengineer|analytics|bigdata|big data|data science|data analytics|data insights|data mining|distributed computing|parallel processing|apache spark|hadoop|hive|airflow|mlflow|apache kafka|hdfs|apache|kafka"
    TWEET_HASH_TAGS = "dataanalysis|AugmentedIntelligence|datascience|machinelearning|rnd|businessintelligence|DigitalTransformation|datamanagement|ArtificialIntelligence"

    FALSE_POSITIVE = "intelligence|business|text|computer|ebook|pdf|ML|AI|DL|learning|big|insights|processing|network|machine|artifical|data|science|parallel|computing|deep|vision|natural|language|data"

    ALL = AI + "|" + ML + "|" + DL + "|" + CV + "|" + NLP + "|" + DATA + "|" + TWEET_HASH_TAGS
    ALL_FP = ALL + "|" + FALSE_POSITIVE

