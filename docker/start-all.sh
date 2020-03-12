#!/usr/bin/env bash

/etc/init.d/ssh start

#https://github.com/bufferings/docker-access-host/blob/master/docker-entrypoint.sh
#Following script helps the container to listen host machine ports with hostname as "host.docker.internal"
HOST_DOMAIN="host.docker.internal"
ping -q -c1 $HOST_DOMAIN > /dev/null 2>&1
if [ $? -ne 0 ]; then
  HOST_IP=$(ip route | awk 'NR==1 {print $3}')
  echo -e "$HOST_IP\t$HOST_DOMAIN" >> /etc/hosts
fi

# Change the default port in container for Postgresql
sed -i 's/5433/5432/g' /etc/postgresql/10/main/postgresql.conf

# Create roles and DBs for our use
service postgresql restart
su -c "psql -c \"CREATE USER hive WITH LOGIN PASSWORD 'hive' \"" postgres
su -c "psql -c \"CREATE DATABASE hive \"" postgres
su -c "psql -c \"grant all privileges on database hive to hive \"" postgres
su -c "psql -c \"\list \"" postgres

su -c "psql -c \"CREATE USER sparkstreaming WITH LOGIN PASSWORD 'sparkstreaming' \"" postgres
su -c "psql -c \"CREATE DATABASE sparkstreamingdb \"" postgres
su -c "psql -c \"grant all privileges on database sparkstreamingdb to sparkstreaming \"" postgres
su -c "psql -c \"\list \"" postgres

# Format the HDFS
$HADOOP_HOME/bin/hdfs namenode -format -nonInteractive

# Setup the Postgresql as our Hive metastore
/opt/binaries/hive/bin/schematool -dbType postgres -initSchema &

# start hdfs
$HADOOP_HOME/sbin/start-dfs.sh
# start yarn
$HADOOP_HOME/sbin/start-yarn.sh

# Create HDFS directory for Hive
hadoop fs -mkdir /tmp
hadoop fs -mkdir /user
hadoop fs -mkdir /user/hive
hadoop fs -mkdir /user/hive/warehouse
hadoop fs -chmod g+w /tmp
hadoop fs -chmod g+w /user/hive/warehouse

# Start Spark standalone cluster
$SPARK_HOME/sbin/start-all.sh

# start supervisord, check supervisor.conf for list of back ground services
/usr/bin/supervisord

