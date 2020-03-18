# Use Case : Dump Tweet data into Data Lake

Read about [Data Lake](https://aws.amazon.com/big-data/datalakes-and-analytics/what-is-a-data-lake/) for understanding purpose.

So we have a data lake setup:
- Bronze Lake : Raw data i.e tweets
- Silver Lake : Preprocessed data like running some kind of NLP stuff like Nammed Entity Recoginition (NER), cleansing etc.,
- Gold Lake   : Data Ready for web application / dash board to consume 


This is the first step for any subsequent use case examples, as you can see it involves multiple services running in the background.

Typical terminal layout:
![](images/guake_example.png)
 
`Twitter API -> Kafka Producer -> Kafka Server -> Spark Structured Streaming with Kafka Consumer -> Parquet Sink -> Bronze Lake`

Note: We pull our container run id with `$(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1)`

To get a new terminal for our docker instance run : `docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash`


```
cd /path/to/ # Local machine
cd /host  # Docker

#[producer] Guake terminal name! 
    bin/start_kafka_producer.sh

#[consumer]
    bin/dump_raw_data_into_bronze_lake.sh

#[hdfs]
    hdfs dfs -ls /tmp/ssp/data/lake/bronze/delta/
```

------------------------------------------------------------------------------------------------------------------------
