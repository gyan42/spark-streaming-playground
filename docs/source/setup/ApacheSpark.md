# Apache Spark
It is highly recommended to setup Hadoop and Hive before Apache Spark.

Download the latest build from http://spark.apache.org/downloads.html

## Local Setup
```
MIRROR=archive.apache.org
SPARK_VERSION=2.4.5
SPARK_VERSION_SUFFIX=-bin-hadoop2.7

mkdir -p /opt/binaries/
cd /opt/binaries/

wget https://${MIRROR}/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}${SPARK_VERSION_SUFFIX}.tgz 
# spark-2.4.5-bin-hadoop2.7
tar xvzf spark-${SPARK_VERSION}${SPARK_VERSION_SUFFIX}.tgz


# add following to ~/.bashrc
export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-amd64/
export SPARK_HOME=/opt/binaries/spark-2.4.5-bin-hadoop2.7/

# switch to the conda env you are in and run `which python` and use the path here
export PYSPARK_PYTHON=/home/mageswarand/anaconda3/envs/vh/bin/python
export PYSPARK_DRIVER_PYTHON=/home/mageswarand/anaconda3/envs/vh/bin/python
export PYTHONDONTWRITEBYTECODE=True
```

## Standalone mode

Rerences: https://spark.apache.org/docs/latest/spark-standalone.html

Following setup was on my machine Dell-G7 which has 32GB RAM and 12 cores :)

```
cd /path/to/spark-streaming-playground
cp config/conf/spark/conf/hive-site.xml /opt/binaries/spark-2.4.5-bin-hadoop2.7/conf/hive-site.xml
cp config/conf/spark/conf/spark-defaults.conf /opt/binaries/spark-2.4.5-bin-hadoop2.7/conf/spark-defaults.conf

cd /opt/binaries/spark-2.4.5-bin-hadoop2.7/
sbin/start-all.sh
sbin/stop-all.sh
```

A [config](https://github.com/gyan42/spark-streaming-playground/tree/master/config/conf) folder is maintained for quick reference, please head there to find related config xml files and move it to your
Spark `conf` folder.  

UI      : http://localhost:8080
MASTER  : spark://IMCHLT276:7077 


## Thrift Server
Thrift server enable REST endpoint to Spark, hosting itself as a running application in the
Spark cluster. It can be thought as a distributed SQL engine with an REST end point.
  
Spark doc [here](https://spark.apache.org/docs/latest/sql-distributed-sql-engine.html)

```
sbin/start-thriftserver.sh \
--master spark://IMCHLT276:7077 \
--hiveconf hive.server2.thrift.bind.host=localhost \
--hiveconf hive.server2.thrift.port=10000 \
--executor-memory 2g \
--conf spark.jars=libs/postgresql-42.2.10.jar \
--conf spark.cores.max=2
```

Test it with `beeline` client, user will be your machine login user and empty password.
 
```
bin/beeline
 !connect jdbc:hive2://localhost:10000

```

## PySpark Integration

`pyspark --master spark://IMCHLT276:7077 --conf "spark.sql.streaming.checkpointLocation=/opt/spark-warehouse/"`


```shell script
#pyspark shell
# https://spark.apache.org/docs/latest/sql-data-sources-hive-tables.html
from pyspark.sql.types import *

cSchema = StructType([StructField("Words", StringType())\
                      ,StructField("total", IntegerType())])

test_list = [['Hello', 1], ['I am fine', 3]]

df = spark.createDataFrame(test_list,schema=cSchema) 

df.createGlobalTempView("test_df")

from pyhive import hive
connection = hive.connection(host="localhost")
df = pd.reqd_sql("show tables", con=connection)
```

**JDBC**

```
beeline> !connect jdbc:hive2://<host>:<port>/<database>?hive.server2.transport.mode=http;hive.server2.thrift.http.path=<http_endpoint>
```


**References**

- https://jaceklaskowski.gitbooks.io/mastering-spark-sql/spark-sql-hive-metastore.html
- https://stackoverflow.com/questions/32730731/error-creating-transactional-connection-factory-during-running-spark-on-hive-pro
- https://aws.amazon.com/premiumsupport/knowledge-center/postgresql-hive-metastore-emr/
- http://www.russellspitzer.com/2017/05/19/Spark-Sql-Thriftserver/
- https://acadgild.com/blog/how-to-access-hive-tables-to-spark-sql
- https://medium.com/@marcovillarreal_40011/creating-a-spark-standalone-cluster-with-docker-and-docker-compose-ba9d743a157f
- https://medium.com/@saipeddy/setting-up-a-thrift-server-4eb0c55c11f0
- https://www.adaltas.com/en/2019/03/25/spark-sql-dataframe-thrift-server/
- https://jaceklaskowski.gitbooks.io/mastering-spark-sql/spark-sql-thrift-server.html
- https://www.adaltas.com/en/2019/03/25/spark-sql-dataframe-thrift-server/


**Learning Materials**
- https://databricks.com/session/monitoring-structured-streaming-applications-using-web-ui
- https://databricks.com/session/a-deep-dive-into-structured-streaming
- https://databricks.com/session/deep-dive-into-monitoring-spark-applications-using-web-ui-and-sparklisteners
- https://databricks.com/blog/2016/07/28/structured-streaming-in-apache-spark.html
- https://blog.clairvoyantsoft.com/productionalizing-spark-streaming-applications-4d1c8711c7b0