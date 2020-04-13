# Apache Hadoop

- First would be setting up the `ssh`, which you can refer [here](ssh.md)
- Having the right version of Java
```
sudo apt-get install openjdk-8-jdk
java -version # 1.8.x.yyy
``` 
- Download the hadoop [3.1.2 version](https://archive.apache.org/dist/hadoop/common/hadoop-3.1.2/hadoop-3.1.2.tar.gz)
- Extract to say `/opt/binaries/hadoop/
```
    tar xzf hadoop-3.1.2.tar.gz
    mv hadoop-3.1.2.tar.gz hadoop
```
- Following files are needed before you can start the service:
    - [hadoop/etc/hadoop/hadoop-env.sh](https://github.com/gyan42/spark-streaming-playground/tree/master/config/conf/hadoop/etc/hadoop)
    - [hadoop/etc/hadoop/core-site.xml](https://github.com/gyan42/spark-streaming-playground/tree/master/config/conf/hadoop/etc/hadoop)
    - [hadoop/etc/hadoop/hdfs-site.xml](https://github.com/gyan42/spark-streaming-playground/tree/master/config/conf/hadoop/etc/hadoop)
    - [hadoop/etc/hadoop/mapred-site.xml](https://github.com/gyan42/spark-streaming-playground/tree/master/config/conf/hadoop/etc/hadoop)
    - [hadoop/etc/hadoop/yarn-site.xml](https://github.com/gyan42/spark-streaming-playground/tree/master/config/conf/hadoop/etc/hadoop)
- `vim ~/.bashrc`
    ```shell script
    export HADOOP_HOME="/opt/binaries/hadoop"
    export PATH=$PATH:$HADOOP_HOME/bin
    export PATH=$PATH:$HADOOP_HOME/sbin 
    export HADOOP_MAPRED_HOME=${HADOOP_HOME}
    export HADOOP_COMMON_HOME=${HADOOP_HOME}
    export HADOOP_HDFS_HOME=${HADOOP_HOME}
    export YARN_HOME=${HADOOP_HOME}
    ```    
- Prepare our HDFS `bin/hdfs namenode -format`
- Start HDFS `/opt/binaries/hadoop/sbin/start-dfs.sh`. Check the url @  [http://localhost:9870](http://localhost:9870)
- Start Yarn `/opt/binaries/hadoop/sbin/start-yarn.sh`. Check the url @ [localhost:8088](localhost:8088)
- Use the command `jps` to see the following list of Java containers running:
    ```
    NameNode
    DataNode
    ResourceManager
    NodeManager
    SecondaryNameNode
    ```

**References**
- https://data-flair.training/blogs/installation-of-hadoop-3-on-ubuntu/
- https://towardsdatascience.com/a-gentle-introduction-to-apache-arrow-with-apache-spark-and-pandas-bb19ffe0ddae
