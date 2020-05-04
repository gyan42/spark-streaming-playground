# Spark ML Model

## Requirements
- Use a offline Tweet Dataset
- Build a sentiment classification model and use it on streams

------------------------------------------------------------------------------------------------------------------------

## Configuration
- [Tweets Keywords Used](https://gyan42.github.io/spark-streaming-playground/build/html/ssp/ssp.utils.html#ssp.utils.ai_key_words.AIKeyWords)
- Config file used : [default_ssp_config.gin](https://github.com/gyan42/spark-streaming-playground/blob/756ee7c204039c8a3bc890a95e1da78ac2d6a9ee/config/default_ssp_config.gin)
- [TwitterProducer](https://gyan42.github.io/spark-streaming-playground/build/html/ssp/ssp.kafka.producer.html)
- [SentimentSparkModel](https://gyan42.github.io/spark-streaming-playground/build/html/ssp/ssp.spark.streaming.ml.html?highlight=sentimentsparkmodel#ssp.spark.streaming.ml.sentiment_analysis_model.SentimentSparkModel)
- [SentimentAnalysis](https://gyan42.github.io/spark-streaming-playground/build/html/ssp/ssp.spark.streaming.analytics.html?highlight=sentimentanalysis#ssp.spark.streaming.analytics.sentiment_analysis.SentimentAnalysis)
- [SentimentSparkModel](https://gyan42.github.io/spark-streaming-playground/build/html/ssp/ssp.spark.streaming.ml.html?highlight=sentimentsparkmodel#ssp.spark.streaming.ml.sentiment_analysis_model.SentimentSparkModel)
------------------------------------------------------------------------------------------------------------------------

## Implementation
- Get the twitter dataset from https://www.kaggle.com/kazanova/sentiment140
- Build a Spark ML pipeline 
- Train a model and store it in HDFS
- Load the model and use them in streams for classification

------------------------------------------------------------------------------------------------------------------------

## How to run?


There are two ways of running, that is on docker or on your local machine. In either case, opening the terminal
is the difference, once the terminal is launched, the steps are common. 

Start the docker container, if needed:
```
docker run -v $(pwd):/host/ --hostname=$(hostname) -p 50075:50075 -p 50070:50070 -p 8020:8020 -p 2181:2181 -p 9870:9870 -p 9000:9000 -p 8088:8088 -p 10000:10000 -p 7077:7077 -p 10001:10001 -p 8080:8080 -p 9092:9092 -it sparkstructuredstreaming-pg:latest
```

To get a new terminal for our docker instance run :   
`docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash`
Note: We pull our container run id with `$(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1)`

This example needs multiple terminals:

On each terminal move to source folder

- If it is on on local machine
```shell script 
# 
cd /path/to/spark-streaming-playground/ 
```

- If you wanted to run on Docker, then 'spark-streaming-playground' is mounted as a volume at `/host/`
```shell script
docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash
cd /host  
```

- [producer] <- custom (guake) terminal name!
``` 
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
vim bin/data/start_kafka_producer.sh
bin/data/start_kafka_producer.sh
```

- [sparkml]
```
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
#builds and stores the model in HDFS
bin/models/build_sentiment_spark_model_offline.sh
# Runs the model against live stream unless configured to HDFS path
bin/analytics/streaming_sentiment_tweet_analysis.sh
```

------------------------------------------------------------------------------------------------------------------------
 
## Take Aways / Learning's 

- TODOs

------------------------------------------------------------------------------------------------------------------------


**References**
- https://github.com/tthustla/setiment_analysis_pyspark/blob/master/Sentiment%20Analysis%20with%20PySpark.ipynb
