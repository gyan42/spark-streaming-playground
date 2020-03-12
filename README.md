# Structured Streaming Playground

The aim of the this project is to create a zoo of Big Data frameworks on a single machine,
where pipelines can be build and tested based on Twitter stream, like to fetch and to store the data in data lake, 
play around with the Spark Structured SQLs for processing, create dataset from live stream for Machine Learning and 
do interactive visualization from the data lake.


## Tools and Frameworks setup

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

Most of the materials are presented as a reference materials based on our setup environment, based on your machine some steps 
may vary.

To make the things simpler there is a `Dockerfile` with cluster components pre-installed.


## Localhost Port Number used

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

On Dell G7 with 12Cores and 32GB, when services are running :)

![](docs/images/machine_load.png)

## Configuration
Check this [file](config.ini). We use Python `configparser` to read the configs from *.ini file.
Choosen for its simpilicity over others.

Read about [Data Lake](https://aws.amazon.com/big-data/datalakes-and-analytics/what-is-a-data-lake/) for understanding purpose.

So we have a data lake setup:
- Bronze Lake : Raw data i.e tweets
- Silver Lake : Preprocessed data like running some kind of NLP stuff like Nammed Entity Recoginition (NER), cleansing etc.,
- Gold Lake   : Data Ready for web application / dash board to consume 

## How to run?

Most of these examples involve multiple services running in the background on different terminals tabs for the pipeline to work.
It is highly recommened to use terminal like [Guake](http://guake-project.org/).
Guake is a background running terminal application in short, preventing you from closing the terminals.


Assuming most of the user would prefer for Docker, the steps provided accordingly.

`cd /path/to/spark-streaming-playground/`

Build the docker with:
```
docker build --network host -f docker/Dockerfile -t sparkstructuredstreaming-pg:latest .
```

Run the docker with:
```
docker run -v $(pwd):/host/ --hostname=$(hostname) -p 5001:5001 -p 5002:5002 -p 50075:50075 -p 50070:50070 -p 8020:8020 -p 2181:2181 -p 9870:9870 -p 9000:9000 -p 8088:8088 -p 10000:10000 -p 7077:7077 -p 10001:10001 -p 8080:8080 -p 9092:9092 -it sparkstructuredstreaming-pg:latest /bin/bash
```
We are mounting current directoy as a volume inside the container, so make sure you trigger from repo base directory,
so that following steps works.

Make a note of the your machine name with command `hostname`, and update the [config.ini](config.ini) `spark master url` with it,
`eg: spark://IMCHLT276:7077`, `IMCHLT276` should be your machine name.

Based on the available memory and core on your machine, you must adjust the Spark cores/RAM memory 0values on *.sh file located in [bin](bin)


**Use Case : Dump Tweet data into Data Lake**

This is the first step for any subsequent use case examples, as you can see it involves multiple services running in the background.

Typical terminal layout:
![](docs/images/guake_example.png)
 
`Twitter API -> Kafka Producer -> Kafka Server -> Spark Structured Streaming with Kafka Consumer -> Parquet Sink -> Bronze Lake`

Note: We pull our container run id with `$(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1)`

```
#[producer]
    docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash
    cd /host/
    bin/start_kafka_producer.sh

#[consumer]
    docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash
    cd /host/
    bin/dump_raw_data.sh
```

**Use Case : Trending Twitter Hash Tags**

`Bronze Lake -> Spark Structured Streaming Parquet Source -> Extract Hash Tags with UDF -> Spark Structured Streaming Postgresql Sink`

`Postgresql -> Flask REST API -> Web Application`

```
#[hashtag]
    docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash
    cd /host/
    bin/trending_tweet_hashtags.sh

#[dashboard]
    docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash
    cd /host/
    bin/dashboard.sh
```
 
Head to http://0.0.0.0:5001/ for live count on the trending #hashtags
 ![](docs/images/trending_tags.png)
 
**Use Case : Scalable REST end point**

- A naive approach for a scalable back end loading the spaCy model (12MB) and serve them over a REST end point with Kubernetes
- A NLP task called NER is done with spaCy

`Bronze Lake -> Spark Structured Streaming Parquet Source -> Extract NER Tags from text with UDF -> Spark Structured Streaming Console Sink`

`Extract NER Tags from text with UDF : Raw Text -> REST API end point -> Kubernetes -> Docker -> Flask -> spaCy -> NER`

```
#[docker/kubernetes]

    docker build --network host -f docker/ner/Dockerfile -t spacy-flask-ner-python:latest .
    docker run -d -p 5000:5000 spacy-flask-ner-python
    # test it to see everything working
    curl -i -H "Content-Type: application/json" -X POST -d '{"text":"Ram read a book on Friday 20/11/2019"}' http://127.0.0.1:5000/spacy/api/v0.1/ner
    # stop all the services/containers
    docker stop $(docker ps | grep spacy-flask-ner-python | cut -d' ' -f1)
    # docker rm $(docker ps -a -q)
    
    sudo minikube start --vm-driver=none 
    
    # note only first time below commands will add the docker file and run its as as service,
    # there on, our service will be started by default when we start the Kubernetes!
    kubectl create -f kubernetes/spacy-flask-ner-python.deployment.yaml 
    kubectl create -f kubernetes/spacy-flask-ner-python.service.yaml
    # on local machine, test it to see everything working
    curl -i -H "Content-Type: application/json" -X POST -d '{"text":"Ram read a book on Friday 20/11/2019"}' http://127.0.0.1:30123/spacy/api/v0.1/ner
    # on docker, test it to see everything working
    curl -i -H "Content-Type: application/json" -X POST -d '{"text":"Ram read a book on Friday 20/11/2019"}' -sS host.docker.internal:30123/spacy/api/v0.1/ner
    # kubernetes restart
    kubectl delete service/spacy-flask-ner-python-service deployment.apps/spacy-flask-ner-python-deployment
    # and then create the services again

#[ner]
    docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash
    cd /host/
    python3 src/ssp/customudf/spacy_ner_udf.py # test it to see everything working
    bin/ner_extraction_using_spacy.sh
```  

![](docs/images/ner_out.png)

**Use Case : Streaming ML Classification with Static Spark Model**

TODO

**Use Case : Streaing ML Classification with Active Learning Model**

TODO
