# Ignore this one..................





#### Apache Ambari
- https://cwiki.apache.org/confluence/display/AMBARI/Installation+Guide+for+Ambari+2.7.5
- https://docs.cloudera.com/HDPDocuments/Ambari-2.7.5.0/bk_ambari-installation/content/ch_Getting_Ready.html
- https://stackoverflow.com/questions/30181154/skipping-some-license-tests-in-maven
- https://docs.cloudera.com/HDPDocuments/Ambari-2.7.3.0/administering-ambari/content/amb_download_the_ambari_repository_on_ubuntu_18.html
- https://www.youtube.com/watch?v=h5_EBZ8vGZ0
- https://askubuntu.com/questions/760896/how-can-i-fix-apt-error-w-target-packages-is-configured-multiple-times

```
sudo apt install libpython-dev
sudo apt install libpython3.7-dev

wget https://www-eu.apache.org/dist/ambari/ambari-2.7.5/apache-ambari-2.7.5-src.tar.gz (use the suggested mirror from above)
tar xfvz apache-ambari-2.7.5-src.tar.gz
cd apache-ambari-2.7.5-src
mvn versions:set -DnewVersion=2.7.5.0.0
 
pushd ambari-metrics
mvn versions:set -DnewVersion=2.7.5.0.0
popd

# note: clean is removed in the following command, to make sure any sccket connection issue doesn't force to 
# rebuild entire package from begining 
# multi thread support -T 8 threads are used to build

mvn -T 8 -B -o -X clean install jdeb:jdeb -DnewVersion=2.7.5.0.0 -DbuildNumber=5895e4ed6b30a2da8a90fee2403b6cab91d19972 -DskipTests -Dpython.ver="python >= 2.6" -Drat.numUnapprovedLicenses=100 

# -rf :ambari-metrics-grafana : dont ignore to add something like this and restart the build
# keep re running the build command and debug it till u see the success message! NO SHORTCUTS!!!
```
### Installation

```
cd ambari-server/target/
sudo apt-get --reinstall install ./ambari-server*.deb
sudo ambari-server setup
sudo ambari-server start

cd - 
cd ambari-agent/target/
sudo apt-get --reinstall install ./ambari-agent*.deb
vim  /etc/ambari-agent/ambari.ini
    [server]
    hostname=localhost
sudo ambari-agent start    

```


```
sudo su
wget -O /etc/apt/sources.list.d/ambari.list http://public-repo-1.hortonworks.com/ambari/ubuntu18/2.x/updates/2.7.3.0/ambari.list
apt-key adv --recv-keys --keyserver keyserver.ubuntu.com B9733A7A07513CAD
apt-get update

sudo vim /etc/ssh/sshd_config
    #Find this line:
    #Change it to:
    PermitRootLogin yes

cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

apt-get install --reinstall openssh-client
apt-get install --reinstall openssh-server
sudo systemctl restart ssh
sudo systemctl restart sshd
sudo service ssh restart
sudo service sshd restart
sudo service ssh status 
ssh localhost

ssh-keygen -t rsa -b 4096 -C "mageswaran1989@gmail.com"

apt-get install ambari-server
apt-get install ambari-agent
apt-get install ambari-metrics-assembly

ambari-server setup
ambari-server start

vim  /etc/ambari-agent/ambari.ini
    [server]
    hostname=localhost
sudo ambari-agent start  
```

Hive metastore on postgresql:
- https://docs.cloudera.com/HDPDocuments/Ambari-2.4.0.0/bk_ambari-reference/content/using_hive_with_postgresql.html
- https://community.cloudera.com/t5/Support-Questions/Unable-to-connect-to-Hive-database-in-postgres-via-Ambari/td-p/230431

```

sudo adduser hive #password hive

sudo su - postgres
    psql #to launch the terminal
    CREATE USER hive WITH PASSWORD 'hive'; # drop user sparkstreaming;
    \du
    CREATE DATABASE hive;
    grant all privileges on database hive to hive;
    \list # to see the DB created
    \q

# change the 3rd colum values to "all"
sudo vim /etc/postgresql/10/main/pg_hba.conf
    # "local" is for Unix domain socket connections only
    local   all   all                                     md5
    # IPv4 local connections:
    host    all   all             127.0.0.1/32            md5
    # IPv6 local connections:
    host    all   all             ::1/128                 md5

    
import psycopg2
conn = psycopg2.connect(host="localhost", port=5432, database="hive", user="hive", password="hive")
```


- https://www.cloudscoop.net/how-to-uninstall-ambari-hadoop-cluster-like-a-pro/
- https://community.cloudera.com/t5/Support-Questions/How-to-Completely-Clean-Remove-or-Uninstall-Ambari-for-Fresh/td-p/95114