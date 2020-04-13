# Apache Hive

Below notes form [here](https://data-flair.training/blogs/apache-hive-installation/)

- Download the [Hive 3.1.2](https://archive.apache.org/dist/hive/hive-3.1.2/apache-hive-3.1.2-bin.tar.gz)
- Locate and move to `/opt/binaries/` and extract
    ```
      tar -xzf apache-hive-3.1.2-bin.tar.gz
      mv apache-hive-3.1.2-bin hive  
    ```
 - Following files are needed before you can start the service:
    - [hive/conf/hive-site.xml](https://github.com/gyan42/spark-streaming-playground/tree/master/config/conf/hive/conf)
    
- Add to the `PATH` variable
    ```
    export HIVE_HOME= “/opt/binaries/hive”
    export PATH=$PATH:$HIVE_HOME/bin
    ``` 
- Make sure Hadoop services are up and running
    ```
    hadoop fs -mkdir /tmp
    hadoop fs -mkdir /user
    hadoop fs -mkdir /user/hive
    hadoop fs -mkdir /user/hive/warehouse
    hadoop fs -chmod g+w /tmp
    hadoop fs -chmod g+w /user/hive/warehouse
    ```
- Head to [postgres hive](Postgres.md) setup
- Start the service `bin/hiveserver2` (this is a service doesn't end, hence needs a terminal!)
- Test the connection with
`bin/beeline -n dataflair -u jdbc:hive2://localhost:10001`
- Start the metastore as service
`hive --service metastore`

**References**
- https://data-flair.training/blogs/apache-hive-installation/
- https://stackoverflow.com/questions/35449274/java-lang-runtimeexception-unable-to-instantiate-org-apache-hadoop-hive-ql-meta
- https://stackoverflow.com/questions/52994585/user-is-not-allowed-to-impersonate-anonymous-state-08s01-code-0-org-apache-had
- https://data-flair.training/blogs/apache-hive-metastore/
- https://mapr.com/docs/61/Hive/Config-RemotePostgreSQLForHiveMetastore.html
- https://www.quora.com/What-is-Hive-Metastore