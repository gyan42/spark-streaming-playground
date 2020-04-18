# How to Run?
 
Most of the materials are presented as a reference materials based on local machine setup environment, 
based on your machine some steps may vary.

Based on the available memory and core on your machine, you must adjust the Spark cores/RAM memory
values on *.sh file located in [bin](https://github.com/gyan42/spark-streaming-playground/tree/master/bin)


## Configuration

We use [Gin-config](https://github.com/google/gin-config) and Python `configparser` to read the configs from *.ini file.

- Add your Twitter credentials @ [twitter_ssp_config.gin](https://github.com/gyan42/spark-streaming-playground/tree/master/config/twitter_ssp_config.gin)
- [default_ssp_config.gin](https://github.com/gyan42/spark-streaming-playground/blob/master/config/default_ssp_config.gin) is used for most of the use case examples.

Update the `spark master url` with the new value in `default_ssp_config.gin`, if you have a different setup than mentioned here.
Spark master url is configured to read the machine `hostname` and construct local Spark master url.
`eg: spark://IMCHLT276:7077`, in the place of `IMCHLT276` you see your machine name.


## On Local Machine
  
### Start Services


- Start the services manually as a background processes (Lookout of errors int he jungle of service logs...)
```
/opt/binaries/hive/bin/hiveserver2 &
/opt/binaries/kafka/bin/zookeeper-server-start.sh /opt/binaries/kafka/config/zookeeper.properties &
/opt/binaries/kafka/bin/kafka-server-start.sh /opt/binaries/kafka/config/server.properties &
/opt/binaries/kafka/bin/kafka-server-start.sh /opt/binaries/kafka/config/server1.properties &
/opt/binaries/kafka/bin/kafka-server-start.sh /opt/binaries/kafka/config/server2.properties &
/opt/binaries/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 10 --topic ai_tweets_topic
/opt/binaries/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 10 --topic mix_tweets_topic
```

- Or you could use [supervisor](http://supervisord.org/) to start all the services, check [docker/supervisor.conf](https://github.com/gyan42/spark-streaming-playground/blob/master/docker/supervisor.conf) for list of back ground services
```
/usr/bin/supervisord -c docker/supervisor.conf # restart if you see any error
```

- Start Spark and Hive services...

```
# start hdfs
$HADOOP_HOME/sbin/start-dfs.sh
# start yarn
$HADOOP_HOME/sbin/start-yarn.sh
# Start Spark standalone cluster
$SPARK_HOME/sbin/start-all.sh
```

To make sure all the services are up and running, execute the command `jps`, you should see the following list:

```
13601 Jps
11923 NameNode
12109 DataNode
12431 SecondaryNameNode
12699 ResourceManager
12919 NodeManager
9292 Kafka
9294 Kafka
10358 Kafka
3475 Main
13338 Master
13484 Worker
```

`HDFS`   : NameNode, DataNode, SecondaryNameNode
`Hadoop` : ResourceManager, NodeManager
`Kafka`  : Kafka, Kafka, Kafka
`Spark`  : Main, Master, Worker

- If you wanna stop playing...
```
/opt/binaries/kafka/bin/kafka-server-stop.sh
/opt/binaries/kafka/bin/zookeeper-server-stop.sh
$HADOOP_HOME/sbin/stop-dfs.sh
$HADOOP_HOME/sbin/stop-yarn.sh
$SPARK_HOME/sbin/stop-all.sh
```
- Activate `ssp` Python environment
```
source activate ssp
```

Since we stop and start Spark Streaming Kafka consumer, restart Kafka server, sometimes the offset can go for a toss.
To solve the issue we need to clear the Kafka data and Spark warehouse data.
 
```
/opt/binaries/kafka/bin/kafka-server-stop.sh
/opt/binaries/kafka/bin/zookeeper-server-stop.sh

/opt/binaries/kafka/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic ai_tweets_topic 
/opt/binaries/kafka/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic mix_tweets_topic
rm -rf /var/lib/zookeeper/
rm -rf /tmp/kafka-logs*
rm -rf /opt/spark-warehouse/
hdfs dfs -rm -r /tmp/ssp/data/lake/checkpoint/
```

From here on you can try the use cases. (Use cases documents too repeat some of these steps for clarity!)

## Docker

- Start the container
```
docker run -v $(pwd):/host/ --hostname=$(hostname) -p 50075:50075 -p 50070:50070 -p 8020:8020 -p 2181:2181 -p 9870:9870 -p 9000:9000 -p 8088:8088 -p 10000:10000 -p 7077:7077 -p 10001:10001 -p 8080:8080 -p 9092:9092 -it sparkstructuredstreaming-pg:latest
```

- Get the bash shell
```
# to get bash shell from running instance
docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash
```

From here on you can try the use cases. (Use cases documents too repeat some of these steps for clarity!)
Twitter App credentials and update it here [twitter_ssp_config.gin](chttps://github.com/gyan42/spark-streaming-playground/blob/master/config/twitter_ssp_config.gin).