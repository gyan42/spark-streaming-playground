# How to Run?
 
Most of the materials are presented as a reference materials based on local machine setup environment, 
based on your machine some steps may vary.

Based on the available memory and core on your machine, you must adjust the Spark cores/RAM memory
values on *.sh file located in [bin](https://github.com/gyan42/spark-streaming-playground/tree/master/bin)


## Configuration

We use [Gin-config](https://github.com/google/gin-config) and Python `configparser` to read the configs from *.ini file.

- Add your Twitter credentials @ [twitter_ssp_config.gin](https://github.com/gyan42/spark-streaming-playground/tree/master/config/twitter_ssp_config.gin)
- [default_ssp_config.gin](https://github.com/gyan42/spark-streaming-playground/blob/master/config/default_ssp_config.gin) is used for most of the use case examples.

Make a note of the your machine name with command `hostname`, and update the `spark master url` with the new value in `default_ssp_config.gin`,
`eg: spark://IMCHLT276:7077`, `IMCHLT276` should be your machine name.


## On Local Machine
  
### Start Services

- swipe out previous run data, if needed!
```
/opt/binaries/kafka/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic ai_tweets_topic 
/opt/binaries/kafka/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic mix_tweets_topic
sudo rm -rf /tmp/kafka-logs 
sudo rm -rf /var/lib/zookeeper/
sudo rm -rf /tmp/kafka-logs*
rm -rf /opt/spark-warehouse/
hdfs dfs -rm -r /tmp/ssp/data/lake/checkpoint/
```

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
sudo /usr/bin/supervisord -c docker/supervisor.conf # restart if you see any error
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

- If you wanna stop playing...
```
sudo /opt/binaries/kafka/bin/kafka-server-stop.sh
sudo /opt/binaries/kafka/bin/zookeeper-server-stop.sh
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
sudo /opt/binaries/kafka/bin/kafka-server-stop.sh
sudo /opt/binaries/kafka/bin/zookeeper-server-stop.sh

sudo rm -rf /tmp/kafka-logs*
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
witter App credentials and update it here [twitter.ini](config/twitter.ini).