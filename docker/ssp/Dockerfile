# We are using Ubuntu as base image
FROM ubuntu:18.04
RUN mkdir /opt/binaries/
RUN mkdir /opt/binaries/hadoop
RUN mkdir /opt/binaries/hive
RUN mkdir /opt/binaries/spark
RUN mkdir /opt/hdfs/

# Binaries
WORKDIR /opt/binaries/
RUN apt-get update
RUN apt-get install -y wget axel vim rsync net-tools

#Any tweaks needed for version, then this is the place to make
RUN wget https://archive.apache.org/dist/hadoop/common/hadoop-3.1.2/hadoop-3.1.2.tar.gz
RUN wget https://archive.apache.org/dist/hive/hive-3.1.2/apache-hive-3.1.2-bin.tar.gz
RUN wget https://archive.apache.org/dist/spark/spark-2.4.4/spark-2.4.4-bin-hadoop2.7.tgz
RUN wget https://downloads.apache.org/kafka/2.4.0/kafka_2.11-2.4.0.tgz

RUN apt-get install -y postgresql postgresql-contrib
RUN apt-get update --fix-missing
RUN apt-get install -y ssh
RUN apt-get install -y supervisor
RUN apt-get install -y openssh-server
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:openjdk-r/ppa
RUN apt-get install -y openjdk-8-jdk
RUN apt-get install -y zookeeperd
RUN apt-get install -y build-essential
RUN apt-get install -y python3-pip zip
RUN apt-get install -y libpq-dev
RUN apt-get install -y iputils-ping
RUN apt-get install -y iproute2
RUN apt-get install -y curl
RUN apt-get install -y libsnappy-dev
#RUN rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME "/usr/lib/jvm/java-1.8.0-openjdk-amd64/"

#COPY data/binaries/hadoop-3.1.2.tar.gz  /opt/binaries/
#COPY data/binaries/apache-hive-3.1.2-bin.tar.gz  /opt/binaries/
#COPY data/binaries/spark-2.4.4-bin-hadoop2.7.tgz /opt/binaries/
#COPY data/binaries/kafka_2.11-2.4.0.tgz /opt/binaries/

RUN mkdir /opt/binaries/kafka

RUN tar xvzf kafka_2.11-2.4.0.tgz -C /opt/binaries/kafka --strip-components=1
RUN tar xzf hadoop-3.1.2.tar.gz -C hadoop/ --strip-components=1
RUN tar xzf apache-hive-3.1.2-bin.tar.gz -C hive/ --strip-components=1
RUN tar xzf spark-2.4.4-bin-hadoop2.7.tgz -C spark/ --strip-components=1
#
##>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# We are gonna use /opt/binaries/ as our base directory for all software, to keep things explicit from other tutorials
ENV HADOOP_HOME "/opt/binaries/hadoop"
ENV PATH $PATH:$HADOOP_HOME/bin
ENV PATH $PATH:$HADOOP_HOME/sbin
ENV HADOOP_MAPRED_HOME ${HADOOP_HOME}
ENV HADOOP_COMMON_HOME ${HADOOP_HOME}
ENV HADOOP_HDFS_HOME ${HADOOP_HOME}
ENV YARN_HOME ${HADOOP_HOME}
ENV ARROW_LIBHDFS_DIR=${HADOOP_HOME}/lib/native

RUN apt-get install -y vim

# Hadoop configs for single node machine
ADD config/conf/hadoop/etc/hadoop/core-site.xml /opt/binaries/hadoop/etc/hadoop/core-site.xml
ADD config/conf/hadoop/etc/hadoop/hadoop-env.sh /opt/binaries/hadoop/etc/hadoop/hadoop-env.sh
ADD config/conf/hadoop/etc/hadoop/hdfs-site.xml /opt/binaries/hadoop/etc/hadoop/hdfs-site.xml
ADD config/conf/hadoop/etc/hadoop/mapred-site.xml /opt/binaries/hadoop/etc/hadoop/mapred-site.xml
ADD config/conf/hadoop/etc/hadoop/yarn-site.xml /opt/binaries/hadoop/etc/hadoop/yarn-site.xml


EXPOSE 9870
EXPOSE 9000
EXPOSE 8088
EXPOSE 5432


#VOLUME ["/opt/hdfs/"]
# To make root user ssh login enabled in container
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config

RUN echo "export JAVA_HOME=$JAVA_HOME" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh && \
    echo "export HDFS_DATANODE_USER=root" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh && \
    echo "export HDFS_NAMENODE_USER=root" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh && \
    echo "export HDFS_SECONDARYNAMENODE_USER=root" >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh
RUN echo "export YARN_RESOURCEMANAGER_USER=root" >> $HADOOP_HOME/etc/hadoop/yarn-env.sh && \
    echo "export YARN_NODEMANAGER_USER=root" >> $HADOOP_HOME/etc/hadoop/yarn-env.sh
RUN ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa && \
    cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys && \
    chmod 0600 ~/.ssh/authorized_keys
##-----------------------------------------------------------------------------------------------------------------------

ENV HIVE_HOME "/opt/binaries/hive"
ENV PATH $PATH:$HIVE_HOME/bin

# Hive configs for single node machine
ADD config/conf/hive/conf/hive-site.xml /opt/binaries/hive/conf/hive-site.xml
EXPOSE 10001

##-----------------------------------------------------------------------------------------------------------------------

ENV SPARK_HOME "/opt/binaries/spark"
ENV PATH $PATH:$SPARK_HOME/bin

# Spark configs for single node machine
ADD config/conf/spark/conf/hive-site.xml /opt/binaries/spark/conf/hive-site.xml
ADD config/conf/spark/conf/spark-defaults.conf /opt/binaries/spark/conf/spark-defaults.conf
EXPOSE 8080
EXPOSE 7077
EXPOSE 10000

#-----------------------------------------------------------------------------------------------------------------------
ADD config/conf/kafka/server.properties /opt/binaries/kafka/config/server.properties
ADD config/conf/kafka/server1.properties /opt/binaries/kafka/config/server1.properties
ADD config/conf/kafka/server2.properties /opt/binaries/kafka/config/server2.properties

ENV KAFKA_HOME "/opt/binaries/kafka/"
ENV PATH "$PATH:${KAFKA_HOME}/bin"
RUN ln -s ${KAFKA_HOME}/config/server.properties /etc/kafka.properties

# configuration of supervisord
EXPOSE 9092 2181 50070 8020 50075

#-----------------------------------------------------------------------------------------------------------------------
# Python specific setup

COPY requirements_docker.txt /opt/binaries/
RUN pip3 install -r /opt/binaries/requirements.txt
ENV PYSPARK_PYTHON /usr/bin/python3
ENV PYSPARK_DRIVER_PYTHON /usr/bin/python3
ENV PYTHONIOENCODING utf8
RUN python3 -m nltk.downloader stopwords
RUN python3 -m spacy download en_core_web_sm

ADD docker/supervisor.conf /etc/supervisor/conf.d/supervisor.conf
ADD docker/start-all.sh /opt/binaries/start-all.sh
RUN chmod 777 /opt/binaries/start-all.sh
RUN chmod 777 /opt/hdfs/

#
#ENV PG_APP_HOME="/etc/docker-postgresql" \
#    PG_VERSION=10 \
#    PG_USER=postgres \
#    PG_HOME=/var/lib/postgresql \
#    PG_RUNDIR=/run/postgresql \
#    PG_LOGDIR=/var/log/postgresql \
#    PG_CERTDIR=/etc/postgresql/certs
#
#ENV PG_BINDIR=/usr/lib/postgresql/${PG_VERSION}/bin \
#    PG_DATADIR=${PG_HOME}/${PG_VERSION}/main

#RUN apt-get update
#RUN apt-get install -y postgresql-client-
ENTRYPOINT ["/opt/binaries/start-all.sh"]








