# Spark ML Model

## Requirements
- Use a offline Tweet Dataset
- Build a sentiment classification model and use it on streams

## Implementation
- Get the twitter dataset from https://www.kaggle.com/kazanova/sentiment140
- Build a Spark ML pipeline 
- Train a model and store it in HDFS
- Load the model and use them in streams for classification

## How to run?
There are two ways of running, that is on docker or on your local machine. In either case, opening the terminal
is the difference, once the terminal is launched, the steps are common. 

To get a new terminal for our docker instance run : `docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash`
Note: We pull our container run id with `$(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1)`

This example needs testing of the API flask server on multiple levels, before using them in Spark Streaming.
Hence the first half details teh steps to test at 3 different levels and in the second part to start the 
Spark Streaming application

```
[sparkml]
    cd /path/to/spark-streaming-playground/ # Local machine
    cd /host  # Docker
    
    unzip data/dataset/sentiment/sentiment140.zip -d data/dataset/sentiment/sentiment140
    #builds and stores the model in HDFS
    bin/models/build_sentiment_spark_model_offline.sh
    # Runs the model against live stream unless configured to HDFS path
    bin/analytics/streaming_sentiment_tweet_analysis.sh
```

## References
- https://github.com/tthustla/setiment_analysis_pyspark/blob/master/Sentiment%20Analysis%20with%20PySpark.ipynb
