# PostgreSQL

https://www.postgresql.org/

Here is a good comparision [PostgreSQL vs MySQL](https://www.postgresqltutorial.com/postgresql-vs-mysql/) 

The choice of PostgresSQL was done since we are using closest managed service in AWS called [Redshift](https://aws.amazon.com/redshift/)
 
## Setup

```
#install ubuntu packages
sudo apt-get install postgresql postgresql-contrib

# check the version
sudo -u postgres psql -c "SELECT version();"

# test the installation
sudo su - postgres
    psql #to launch the terminal
    \q #to quit

# or to run psql directly
sudo -i -u postgres psql

```

To cut short the permission configurations for new users, lets create a Ubuntu user with same name: 
`sudo adduser sparkstreaming #password sparkstreaming` 

We need log into PostgresSQL to create users before they can use the DB.
For our case we are going ot create a user called `sparkstreaming` and DB called `sparkstreamingdb`

```
sudo su - postgres
    psql #to launch the terminal
    # drop user sparkstreaming;
    CREATE USER sparkstreaming WITH PASSWORD 'sparkstreaming'; 
    \du #list users
    CREATE DATABASE sparkstreamingdb;
    grant all privileges on database sparkstreamingdb to sparkstreaming;
    \list # to see the DB created
    \q

# test the new user and DB
sudo -i -u sparkstreaming  psql -d sparkstreamingdb
    CREATE TABLE authors (code char(5) NOT NULL, name varchar(40) NOT NULL, city varchar(40) NOT NULL, joined_on date NOT NULL, PRIMARY KEY (code));
    INSERT INTO authors VALUES(1,'Ravi Saive','Mumbai','2012-08-15');
    \dt #list tables
    \conninfo #get connection info
```

If you would like to restart the service:

```
sudo service postgresql restart
sudo systemctl restart postgresql
```

To see how many active connections to the DB are made:
`SELECT pid, application_name, state FROM pg_stat_activity;`
This is important some times the connetion becomes stale and left hanging there, making new connection bounce back.

## Integration with Spark

Part of our work flow we need to read and write to Postresql from Apache Spark. 
Lets test whether we can do it from local `pyspark` terminal.

```
#it is mandate to give the posgres maven ids for runtime
pyspark --packages postgresql:postgresql:9.1-901-1.jdbc4

#read the table "authors" 
df = spark.read. \
    format("jdbc"). \
    option("url", "jdbc:postgresql://localhost:5432/sparkstreamingdb"). \
    option("dbtable", "authors"). \
    option("user", "sparkstreaming"). \
    option("password", "sparkstreaming"). \
    option("driver", "org.postgresql.Driver"). \
    load()

# display the table
df.printSchema()
```

## Hive Metastore DB setup

We could use different metastore DB for Hive, below steps helps to use Postgresql as its external metastore,
which then can be shared with Spark.

```
sudo adduser hive #password hive

sudo su - postgres
    psql #to launch the terminal
    CREATE USER hive WITH PASSWORD 'hive'; # drop user hive; (if needed)
    \du
    CREATE DATABASE hive;
    grant all privileges on database hive to hive;
    \list # to see the DB created
    \q
```

We need do some changes to connection configs, to enable login from different services:

```
# change the 3rd colum values to "all"
sudo vim /etc/postgresql/10/main/pg_hba.conf
    # "local" is for Unix domain socket connections only
    local   all   all                                     md5
    # IPv4 local connections:
    host    all   all             127.0.0.1/32            md5
    # IPv6 local connections:
    host    all   all             ::1/128                 md5

```

Fire a python shell and test out the connection

```    
import psycopg2
conn = psycopg2.connect(host="localhost", port=5432, database="hive", user="hive", password="hive")
sql_command = "SELECT * FROM \"CDS\";"
print (sql_command)
# Load the data
data = pd.read_sql(sql_command, conn)
print(data)
```

Use Hive provided tool to setup the metastore tables an schema:
`/path/to/hive/bin/schematool -dbType postgres -initSchema`

And then try running following commands, you should see bunch of tables there:
```shell script
sudo -i -u hive  psql -d hive
#asks for two password, one for sudo and other one for DB `hive` which is `hive`
    hive=> \dt
```


**References**
- https://www.tecmint.com/install-postgresql-on-ubuntu/
- https://linuxize.com/post/how-to-install-postgresql-on-ubuntu-18-04/
- https://medium.com/@thomaspt748/how-to-upsert-data-into-relational-database-using-spark-7d2d92e05bb9
- https://linuxize.com/post/how-to-create-a-sudo-user-on-ubuntu/
- https://stackoverflow.com/questions/21898152/why-cant-you-start-postgres-in-docker-using-service-postgres-start
- https://markheath.net/post/exploring-postgresql-with-docker




