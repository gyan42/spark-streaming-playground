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
```
```
# add following to ~/.bashrc
export KAFKA_HOME="/opt/kafka/"
export PATH="$PATH:${KAFKA_HOME}/bin"

sudo ln -s $KAFKA_HOME/config/server.properties /etc/kafka.properties
sudo kafka-server-start.sh /etc/kafka.properties

#to create a topic
kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic twitter_data

#to delete the topic
sudo /opt/binaries/kafka/bin/kafka-server-stop.sh
sudo rm -rf /tmp/kafka-logs 
vim /etc/kafka.properties
    delete.topic.enable = true

kafka-topics.sh --delete --zookeeper localhost:2181 --topic twitter_data
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

## Test with our code
```
cd {project_root}/ 
export PYTHONPATH=$(pwd)/src/:$PYTHONPATH
python src/dataset/tweet_dataset.py --mode=start_tweet_stream
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic twitter_data --from-beginning
```
