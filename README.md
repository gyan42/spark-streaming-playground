# Structured Streaming Playground

The aim of the this project is to create a zoo of Big Data frameworks on a single machine,
where pipelines can be build and tested based on Twitter stream. Which involves but not limited to fetch,
store the data in data lake, play around with the Spark Structured SQLs for processing, create dataset from live 
stream for Machine Learning and do interactive visualization from the data lake.

## Pipeline Examples and Use Cases  

Run pytest to check everything works fine...
```
pytest -s
pytest -rP #shows the captured output of passed tests.
pytest -rx #shows the captured output of failed tests (default behaviour).
``` 

- [Dump Tweet data into Data Lake](docs/source/usecases/1_dump_tweets.md)  
- [Trending Twitter Hash Tags](docs/source/usecases/2_trending_tweets.md)  
- [Scalable REST end point](docs/source/usecases/3_scalable_rest_api.md)  
- [Streaming ML Classification with Static Spark Model](docs/source/usecases/4_spark_ml.md)
- [Spark SQL Exploration with Stackoverflow dataset](docs/source/usecases/5_static_table_stackoverflow.md)
- [Text Classification with Data Collection](docs/source/usecases/6_full_ml_model_cycle.md)  



## Tools and Frameworks setup

------------------------------------------------------------------------------------------------------------------------

![](docs/source/drawio/big_data_zoo.png)

------------------------------------------------------------------------------------------------------------------------

Assuming that there is some idea of each components, lets cook up some use cases matching the real world project scenarios.
These examples may seem simple or already been explained somewhere else on the web, however care has been taken such that the 
use cases exploit the `scalable` nature on each framework. 

Our setup is configured to run on single machine, however with little bit of effoer same example applications 
can scale to hundreads of nodes and GigaBytes of data by tuning the configurations of respective frameworks involved.

Most of these examples involve multiple services running in the background on different terminal tabs for the pipeline to work.
It is highly recommened to use application like [Guake](http://guake-project.org/).
Guake is a background running terminal application in short, preventing you from closing the terminals.

- **Local Machine Setup**

    - [Linux Machine](docs/source/setup/Linux.md)
    - [Anaconda](docs/source/setup/Anaconda.md)
    - [SSH](docs/source/setup/ssh.md)
    - [PostgreSQL](docs/source/setup/Postgres.md)
    - [Apache Hadoop](docs/source/setup/ApacheHadoop.md)
    - [Apache Hive](docs/source/setup/ApacheHive.md)
    - [Apache Spark](docs/source/setup/ApacheSpark.md)
    - [Apache Kafka](docs/source/setup/ApacheKafka.md)
    - [Python libs](requirements.txt)
    - [Docker](docs/source/setup/Docker.md)
    - [Kubernets](docs/source/setup/Kubernetes.md)
    - [Twitter API](https://www.toptal.com/apache/apache-spark-streaming-twitter) Read the link to get ur [API keys](https://developer.twitter.com/)
        - In the heart we depend on Twitter tweet stream.
        - Twitter API along with `Tweepy` package is used to pull the tweets from internet
    
    These steps will help you to turn your machine into a single node cluster (both master and client services will be running on your machine).
    This is pretty heavy stuff to hold on average single machine, so it would be ideal to have RAM `16GB` and `8Cores` minimum. 
    
    Most of the materials are presented as a reference materials based on local machine setup environment, 
    based on your machine some steps may vary.
    
    ```
    # swipe out previous run data, if needed!
    /opt/binaries/kafka/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic ai_tweets_topic 
    /opt/binaries/kafka/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic mix_tweets_topic
    sudo rm -rf /tmp/kafka-logs 
    sudo rm -rf /var/lib/zookeeper/
    sudo rm -rf /tmp/kafka-logs*
    rm -rf /opt/spark-warehouse/
    hdfs dfs -rm -r /tmp/ssp/data/lake/checkpoint/

    
    # Lookout of errors int he jungle of service logs...
    /opt/binaries/hive/bin/hiveserver2 &
    /opt/binaries/kafka/bin/zookeeper-server-start.sh /opt/binaries/kafka/config/zookeeper.properties &
    /opt/binaries/kafka/bin/kafka-server-start.sh /opt/binaries/kafka/config/server.properties &
    /opt/binaries/kafka/bin/kafka-server-start.sh /opt/binaries/kafka/config/server1.properties &
    /opt/binaries/kafka/bin/kafka-server-start.sh /opt/binaries/kafka/config/server2.properties &
    /opt/binaries/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 10 --topic ai_tweets_topic
    /opt/binaries/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 10 --topic mix_tweets_topic

    #or
    
    # use start supervisord, check docker/supervisor.conf for list of back ground services
    sudo /usr/bin/supervisord -c docker/supervisor.conf # restart if you see any error
    ```
    
    Start Spark and Hive services...
    
    ```
    # start hdfs
    $HADOOP_HOME/sbin/start-dfs.sh
    # start yarn
    $HADOOP_HOME/sbin/start-yarn.sh
    # Start Spark standalone cluster
    $SPARK_HOME/sbin/start-all.sh
    ```
  
    If you wanna stop playing...
    ```
    sudo /opt/binaries/kafka/bin/kafka-server-stop.sh
    sudo /opt/binaries/kafka/bin/zookeeper-server-stop.sh
    $HADOOP_HOME/sbin/stop-dfs.sh
    $HADOOP_HOME/sbin/stop-yarn.sh
    $SPARK_HOME/sbin/stop-all.sh
    ```

- **Python Envronment setup**

    Follow the steps [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html) to install `conda`.
    
    ```
    conda create --prefix=/opt/envs/ssp/ python=3.7
    conda activate /opt/envs/ssp
    pip install -r requirements.txt
    source activate ssp
    ```
    
    In general switch to a python environment with all needed packages and run any *.sh files present in [bin](bin)

- **Docker Setup**

    To make the things simpler there is a `Dockerfile` with cluster components pre-installed.
    
    `cd /path/to/spark-streaming-playground/`
    
    Build the docker with:
    ```
    docker build --network host -f docker/Dockerfile -t sparkstructuredstreaming-pg:latest .
    ```
    
    Run the docker with:
    ```
    docker run -v $(pwd):/host/ --hostname=$(hostname) -p 5001:5001 -p 5002:5002 -p 50075:50075 -p 50070:50070 -p 8020:8020 -p 2181:2181 -p 9870:9870 -p 9000:9000 -p 8088:8088 -p 10000:10000 -p 7077:7077 -p 10001:10001 -p 8080:8080 -p 9092:9092 -it sparkstructuredstreaming-pg:latest /bin/bash
    ```
    
    We are mounting current directory as a volume inside the container, so make sure you trigger from repo base directory,
    so that following steps works.
    
    Based on the available memory and core on your machine, you must adjust the Spark cores/RAM memory
     values on *.sh file located in [bin](bin)


------------------------------------------------------------------------------------------------------------------------

### Configuration
Check this [file](config/config.ini). We use Python `configparser` to read the configs from *.ini file.
Choosen for its simpilicity over others.

Make a note of the your machine name with command `hostname`, and update the [config.ini](config/config.ini) `spark master url` with it,
`eg: spark://IMCHLT276:7077`, `IMCHLT276` should be your machine name.

Get the Twitter App credentials and update it here [twitter.ini](config/twitter.ini).

------------------------------------------------------------------------------------------------------------------------

### Debugging

Since we stop and start Spark Streaming Kafka consumer, restart Kafka server, sometimes the offset can go for a toss.

To solve the issue we need to clear the Kafka data and Spark warehouse data.
 
```
sudo /opt/binaries/kafka/bin/kafka-server-stop.sh
sudo /opt/binaries/kafka/bin/zookeeper-server-stop.sh

sudo rm -rf /tmp/kafka-logs*
rm -rf /opt/spark-warehouse/
hdfs dfs -rm -r /tmp/ssp/data/lake/checkpoint/
```

Now head back to **Local Machine Setup** ans start kafka related services.

 
------------------------------------------------------------------------------------------------------------------------

