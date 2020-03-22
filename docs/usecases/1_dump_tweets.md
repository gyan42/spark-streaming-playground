# Use Case : Dump Tweet data into Data Lake

## Requiremetns  

- Come up with [Data Lake](https://aws.amazon.com/big-data/datalakes-and-analytics/what-is-a-data-lake/)  
- Listen to Twitter streams, collect tweets that talk about `Data Science/AI/Machine Learning/Big Data` and dump into bronze lake.

------------------------------------------------------------------------------------------------------------------------

## Implementation
  
So we have a data lake setup as follows on our HDFS, basically boils down to HDFS paths:
- Bronze Lake : Raw data i.e tweets
- Silver Lake : Preprocessed data like running some kind of NLP stuff like Nammed Entity Recoginition (NER), cleansing etc.,
- Gold Lake   : Data Ready for web application / dash board to consume 


- Get API Credentials from Twitter Developement Site  
- Setup Tweepy to read Twitter stream filtering tweets taht talks about `Data Science/AI/Machine Learning/Big Data`  
- Create Kafka topic for twitter stream  
- Dump the tweets from Tweepy into Kafka topic  
- Use Spark Structured Streaming to read the Kafka topic and store as parquet in HDFS  
- Use HDFS command line ot verify the data dump  


Below is the data flow path:

 
`Twitter API -> Kafka Producer -> Kafka Server -> Spark Structured Streaming with Kafka Consumer -> Parquet Sink -> Bronze Lake`

------------------------------------------------------------------------------------------------------------------------

## How to run?

There are two ways of running, that is on docker or on your local machine. In either case, opening the terminal
is the difference, once the terminal is launched, the steps are common. 

To get a new terminal for our docker instance run : `docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash`
Note: We pull our container run id with `$(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1)`

This example needs three terminals:

- Producer [bin/start_kafka_producer.sh](../../bin/start_kafka_producer.sh)
    - `Twitter API -> Kafka Producer -> Kafka Server`
    - [src/ssp/dataset/twiteer_stream_ingestion_main.py](../../src/ssp/dataset/twiteer_stream_ingestion_main.py)    
- Consumer [bin/dump_raw_data_into_bronze_lake.sh](../../bin/dump_raw_data_into_bronze_lake.sh)
    - `Spark Structured Streaming with Kafka Consumer -> Parquet Sink -> Bronze Lake`
    - [src/ssp/dataset/twiteer_stream_ingestion_main.py](../../src/ssp/dataset/twiteer_stream_ingestion_main.py)
    - `spark-submit` is used to run the application.
    - Which submits the application to Spark master, if the application has SparkSession in it, then it will
      be considered as Spark Application and the cluster is used to run the application
    - Since cluster is involved in our example, we need to specify the number of cores, memory needed and maximum cores for our application,
      which is exported just before the spark-submit command in the shell script file.
    - Also the extra packages need for the application is given as part of the submit config
- HDFS 
    - Command line tool to test the parquet file storage
    
```
cd /path/to/spark-streaming-playground/ # Local machine
cd /host  # On Docker 'spark-streaming-playground' is mountes as a volume at /host/

#[producer] Guake terminal name! 
    bin/start_kafka_producer.sh

#[consumer]
    bin/dump_raw_data_into_bronze_lake.sh

#[hdfs]
    hdfs dfs -ls /tmp/ssp/data/lake/bronze/delta/
```

------------------------------------------------------------------------------------------------------------------------

## Take Aways / Learning's 
- Understand how to get an Twitter API
- Learn to use Python library Tweepy to listen to Twitter stream
    - http://docs.tweepy.org/en/latest/streaming_how_to.html
- Understand to use Apache Kafka topic
    - `sudo /opt/binaries/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 20 --topic twitter_data` 
- Dumping the data to Kafka topic : [TweetsListener](../../src/ssp/dataset/twiteer_stream_ingestion_main.py)
    - Define `KafkaProducer` with Kafka master url
    - Send the data to specific topic
- Using Spark Structured Streaming to read Kafka topic
    - Configuring the read stream
    - Defining the Schema as per [Twitter Json schema](https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object)
- Using Spark Structured Streaming to store streaming data as parquet in HDFS
- View the data with HDFS commands
    

