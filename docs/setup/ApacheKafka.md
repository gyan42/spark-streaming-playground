#Apache Kafka

Get to know about Kafka [here](https://intellipaat.com/blog/what-is-apache-kafka/)

## Setup
```
# To install zookeeper, run the following command:
sudo apt-get install zookeeperd

# Testing
sudo systemctl status zookeeper
sudo systemctl start zookeeper
sudo systemctl enable zookeeper

sudo apt-get install net-tools
# Now you can run the following command to check whether zookeeper is running on port 2181.
sudo netstat -tulpen | grep 2181

# Zookepr cleanup
sudo systemctl stop zookeeper
# vim /etc/zookeeper/conf_example/zoo.cfg
sudo rm -rf /var/lib/zookeeper/

# kafka
cd /opt/binaries/
wget https://downloads.apache.org/kafka/2.4.0/kafka_2.11-2.4.0.tgz
tar xvzf kafka_2.11-2.4.0.tgz -C /opt/binaries/kafka --strip-components=1
cp spark-streaming-playground/docs/conf/kafka/server1.properties /opt/binaries/kafka/config/server1.properties
cp spark-streaming-playground/docs/conf/kafka/server2.properties /opt/binaries/kafka/config/server2.properties

```
```
# add following to ~/.bashrc
export KAFKA_HOME="/opt/kafka/"
export PATH="$PATH:${KAFKA_HOME}/bin"

# create 3 brokers for more parallelism
sudo /opt/binaries/kafka/bin/kafka-server-start.sh /opt/binaries/kafka/config/server.properties
sudo /opt/binaries/kafka/bin/kafka-server-start.sh /opt/binaries/kafka/config/server1.properties
sudo /opt/binaries/kafka/bin/kafka-server-start.sh /opt/binaries/kafka/config/server2.properties


#to create a topic
sudo /opt/binaries/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 10 --topic ai_tweets_topic

#to delete the topic
sudo /opt/binaries/kafka/bin/kafka-server-stop.sh
sudo rm -rf /tmp/kafka-logs 
vim /etc/kafka.properties
    delete.topic.enable = true

kafka-topics.sh --delete --zookeeper localhost:2181 --topic ai_tweets_topic
```

**Testing**

```
kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic testing
kafka-console-producer.sh --broker-list localhost:9092 --topic testing

kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic testing --from-beginning
```

## References
- https://linuxhint.com/install-apache-kafka-ubuntu/
- https://www.digitalocean.com/community/tutorials/how-to-install-apache-kafka-on-ubuntu-18-04
- https://github.com/vaquarkhan/Apache-Kafka-poc-and-notes
- https://www.michael-noll.com/blog/2013/03/13/running-a-multi-broker-apache-kafka-cluster-on-a-single-node/

## Test with our code
```
cd {project_root}/ 
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
python src/dataset/tweet_dataset.py --mode=start_tweet_stream
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic ai_tweets_topic --from-beginning
```
