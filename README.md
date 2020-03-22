# Structured Streaming Playground

The aim of the this project is to create a zoo of Big Data frameworks on a single machine,
where pipelines can be build and tested based on Twitter stream. Which involves but not limited to fetch,
store the data in data lake, play around with the Spark Structured SQLs for processing, create dataset from live 
stream for Machine Learning and do interactive visualization from the data lake.


## Tools and Frameworks setup

Most of these examples involve multiple services running in the background on different terminals tabs for the pipeline to work.
It is highly recommened to use terminal like [Guake](http://guake-project.org/).
Guake is a background running terminal application in short, preventing you from closing the terminals.

- **Local Machine Setup**

    - [Linux Machine](docs/Linux.md)
    - [Anaconda](docs/Anaconda.md)
    - [SSH](docs/ssh.md)
    - [PostgreSQL](docs/Postgres.md)
    - [Apache Hadoop](docs/ApacheHadoop.md)
    - [Apache Hive](docs/ApacheHive.md)
    - [Apache Spark](docs/ApacheSpark.md)
    - [Apache Kafka](docs/ApacheKafka.md)
    - [Python libs](requirements.txt)
    - [Docker](docs/Docker.md)
    - [Kubernets](docs/Kubernetes.md)
    - [Twitter API](https://www.toptal.com/apache/apache-spark-streaming-twitter) Read the link to get ur [API keys](https://developer.twitter.com/)
        - In the heart we depend on Twitter tweet stream.
        - Twitter API along with `Tweepy` package is used to pull the tweets from internet
    
    These steps will help you to turn your machine into a single node cluster (both master and client services will be running on your machine).
    This is pretty heavy stuff to hold on average single machine, so it would be ideal to have RAM `16GB` and `8Cores` minimum. 
    
    Most of the materials are presented as a reference materials based on local machine setup environment, 
    based on your machine some steps may vary.
    
    ```
    sudo rm -rf /tmp/kafka-ogs 
    sudo rm -rf /var/lib/zookeeper/
    
    /opt/binaries/hive/bin/hiveserver2 &
    sudo /opt/binaries/kafka/bin/zookeeper-server-start.sh /opt/binaries/kafka/config/zookeeper.properties &
    sudo /opt/binaries/kafka/bin/kafka-server-start.sh /etc/kafka.properties &
    sudo /opt/binaries/kafka/bin/kafka-topics.sh --delete --zookeeper localhost:2181 --topic twitter_data 
    sudo /opt/binaries/kafka/bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 20 --topic twitter_data
    
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

- **Localhost Port Number used**

    Here is the list of services and their port numbers...
    
    |Port Number| Service            | Url|
    |------------|-------------------|-----|
    |8080        |Spark UI           |http://localhost:8080|
    |7077        |Spark Master       |spark://IMCHLT276:7077|
    |10000       |Spark Thrift Server|hive2://localhost:10000|
    |10001       |Hive Thrift Server |hive2://localhost:10001|
    |9870        |HDFS UI            |http://localhost:9870|
    |9000        |HDFS IPC           |http://localhost:9000|
    |8088        |Yarn UI            |http://localhost:8088|
    |5432        |PostgreSQL         |postgresql://localhost:5432|
    |5000        |Flask-NER         |http://localhost:5000|
    |5001        |Flask-Dashboard   |http://localhost:5001|
    |5000        |Flask-Tagger      |http://localhost:5002|
    |8888        |Jupyter Lab       |http://localhost:8888/lab|
    |30123       |Kubernetes Load Balancer - NER|http://127.0.0.1:30123
    
    All the services when running could load your machine to the fullest.
    Minimum configuration would be 8+Cores and 32GB, when services are running :)


## Configuration
Check this [file](config.ini). We use Python `configparser` to read the configs from *.ini file.
Choosen for its simpilicity over others.

Make a note of the your machine name with command `hostname`, and update the [config.ini](config.ini) `spark master url` with it,
`eg: spark://IMCHLT276:7077`, `IMCHLT276` should be your machine name.

Get the Twitter App credentials and update it here [twitter.ini](twitter.ini).

------------------------------------------------------------------------------------------------------------------------

### Debugging

In case you see any error with Spark Structured Streaming run:
```
rm -rf /tmp/kafka-logs/
rm -rf /tmp/ssp/raw_data/
rm -rf /opt/spark-warehouse/
hdfs dfs -rm -r /tmp/ssp/data/lake/checkpoint/
```

------------------------------------------------------------------------------------------------------------------------

### Contents

Below are some Big Data frameworks and cool materials to begin with, 
if you are an intermediate or experienced developer you can ignore it.

**Big Data**
    - [Gentle Intro Big Data Frameworks in 20 mins](https://www.youtube.com/watch?v=DCaiZq3aBSc)
    - [Intro](https://towardsdatascience.com/a-brief-summary-of-apache-hadoop-a-solution-of-big-data-problem-and-hint-comes-from-google-95fd63b83623)
    - [Apache Hadoop](https://hadoop.apache.org/)
        - [10mins Read](https://www.guru99.com/learn-hadoop-in-10-minutes.html)
        - [1 day Simplilearn Full Course](https://www.youtube.com/watch?v=5zJt9qAe01w)
        - [HDFS Explained](https://www.youtube.com/watch?v=GJYEsEEfjvk)
    - [Apache Spark](https://spark.apache.org/docs/latest/)
        - [My own post on Spark Jargons](https://medium.com/@mageswaran1989/spark-jargon-for-starters-af1fd8117ada)
        - [RDD Basics](http://homepage.cs.latrobe.edu.au/zhe/ZhenHeSparkRDDAPIExamples.html)
        - [DataFrame/Dataset Basics](https://medium.com/swlh/spark-dataset-apis-a-gentle-introduction-108cdeafdea5)
        - [Spark Streaming](https://spark.apache.org/docs/latest/streaming-programming-guide.html)
        - [Spark Structured Streaming](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
        - [1 day Edureka Full Course](https://www.youtube.com/watch?v=F8pyaR4uQ2g)
    - [Apache Kafka](https://kafka.apache.org/)
        - [what you need to know?](https://intellipaat.com/blog/what-is-apache-kafka/)
        - [Kafka + Apache Spark](https://www.youtube.com/watch?v=65lHphtrfo0)
    - [Apache Hive](https://hive.apache.org/)
        - [Simpilearn 2 hrs Course](https://www.youtube.com/watch?v=rr17cbPGWGA)
    - [Postgresql](https://www.postgresql.org/)
        - [freecodecamp Full Course](https://www.youtube.com/watch?v=qw--VYLpxG4)
    - [Python](https://www.python.org/)
        - [Anaconda](https://www.youtube.com/watch?v=beh7GE4FdnM)
        - [12 hrs course from Edureka](https://www.youtube.com/watch?v=beh7GE4FdnM)
    - Machine Learning
        - [Edureka 12 hours Course](https://www.youtube.com/watch?v=GwIo3gDZCVQ)
        - [Simpilearn 6 hours Course](https://www.youtube.com/watch?v=9f-GarcDY58)

Assuming that there is some idea of each components, lets cook up some use cases matching the real world project scenarios.
These examples may seem simple or already been explained somewhere else on the web, however care has been taken such that the 
use cases exploit the `scalable` nature on each framework. 

Our setup is configured to run on single machine, however with little bit of learning curve and trial & error 
the same example applications can scale to hundreads of nodes and GigaBytes of data with right set of confgiurations
with each framework involved.

**Pipeline Examples and Use Cases** 
    - [Dump Tweet data into Data Lake](docs/usecases/1_dump_tweets.md)
    - [Trending Twitter Hash Tags](docs/usecases/2_trending_tweets.md)
    - [Scalable REST end point](docs/usecases/3_scalable_rest_api.md)
    - Streaming ML Classification with Static Spark Model
    - [Streaming ML Classification with Active Learning Model](docs/usecases/full_ml_model_cycle.md)
