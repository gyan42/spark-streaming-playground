# Docker

## Setup

[- https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)
- [https://docs.docker.com/engine/reference/builder/](https://docs.docker.com/engine/reference/builder/)
```
sudo apt  install docker.io
```


Since docker gonna eat up lot of disk space, it is idel to use HDD instead of SSD in case if you happened to ahve one! 
Below are the steps to update the `root folder` of Docker download path to store the files.

```
sudo systemctl stop docker

sudo mv /var/lib/docker/ /opt/binaries/
sudo rm -rf /var/lib/docker
sudo ln -s /opt/binaries/docker/ /var/lib/docker

sudo vim /etc/docker/daemon.json\:

    {
        “data-path”: “/opt/binaries/docker”,
        “graph”: “/opt/binaries/docker”
    } 

sudo systemctl daemon-reload
sudo systemctl restart docker

sudo ls /opt/binaries/docker
    mageswarand@IMCHLT276:/opt/binaries/docker$ ls
    builder  buildkit  containers  image  network  overlay2  plugins  runtimes  swarm  tmp  trust  volumes

```

It is very common to face network issues with docker, better equip with the basics @ [https://pythonspeed.com/articles/docker-connection-refused/](https://pythonspeed.com/articles/docker-connection-refused/)

## Build our images

**NER Image**

```
docker build --network host -f docker/api/Dockerfile -t spacy-flask-ner-python:latest .
# start the app
docker run -it spacy-flask-ner-python:latest /bin/bash
docker run -d -p 5000:5000 spacy-flask-ner-python
# on a seprate terminal
curl -i -H "Content-Type: application/json" -X POST -d '{"text":"Ram read a book on Friday 20/11/2019"}' http://127.0.0.1:5000/spacy/api/v0.1/ner
```

**Structured Streaming Image**

- Build
```
docker build --network host -f docker/ssp/Dockerfile -t sparkstructuredstreaming-pg:latest .
```

- Run
```
docker run -v $(pwd):/host/ --hostname=$(hostname) -p 50075:50075 -p 50070:50070 -p 8020:8020 -p 2181:2181 -p 9870:9870 -p 9000:9000 -p 8088:8088 -p 10000:10000 -p 7077:7077 -p 10001:10001 -p 8080:8080 -p 9092:9092 -it sparkstructuredstreaming-pg:latest
```

- Login into bash shell:
```
# first time
docker run -v $(pwd):/host/ --hostname=$(hostname) -p 50075:50075 -p 50070:50070 -p 8020:8020 -p 2181:2181 -p 9870:9870 -p 9000:9000 -p 8088:8088 -p 10000:10000 -p 7077:7077 -p 10001:10001 -p 8080:8080 -p 9092:9092 -it sparkstructuredstreaming-pg:latest /bin/bash

# to get bash shell from running instance
docker exec -it $(docker ps | grep sparkstructuredstreaming-pg | cut -d' ' -f1) bash
```

We are mounting current directory as a volume inside the container, so make sure you trigger from repo base directory,
so that following steps works.

## Misc 

**Common commands**

- https://www.edureka.co/blog/docker-commands/

- start the services
```
sudo service docker start
or 
systemctl start docker
systemctl enable docker
```

- build the image
```
docker build --network host -f docker/api/Dockerfile -t spacy-flask-ner-python:latest .
```

- run docker in interactive mode
```
docker run -ti spacy-flask-ner-python /bin/bash
```

- start the app
```
docker run -d -p 5000:5000 spacy-flask-ner-python
```

- list containers
```
docker container ls -a
```

- remove/delete Docker images
```
docker rmi id#
docker images -f dangling=true
docker system prune
docker images purge
```

- stop all the services/containers
```
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
```

- When there is a change in the python code base, we obviously have to 
rebuild the docker image, isn't? Use following steps to do so:
```shell script
docker container ls
docker stop {id}
docker rm {id}
docker build ...
# for multiple shells for same container
docker exec -it <container> bash

```

**Mount Host Folder**
- [https://stackoverflow.com/questions/23439126/how-to-mount-a-host-directory-in-a-docker-container](https://stackoverflow.com/questions/23439126/how-to-mount-a-host-directory-in-a-docker-container)

```
sudo apt-get install virtualbox-guest-x11
sudo mount -t vboxsf /opt/vlab/spark-streaming-playground/ /mnt/dockerfolder
```




**References**

- [https://www.bogotobogo.com/DevOps/DevOps-Kubernetes-1-Running-Kubernetes-Locally-via-Minikube.php](https://www.bogotobogo.com/DevOps/DevOps-Kubernetes-1-Running-Kubernetes-Locally-via-Minikube.php)
- https://blog.adriel.co.nz/2018/01/25/change-docker-data-directory-in-debian-jessie/
- https://rominirani.com/docker-tutorial-series-part-7-data-volumes-93073a1b5b72
- https://medium.com/rahasak/kafka-and-zookeeper-with-docker-65cff2c2c34f
- https://github.com/sameersbn/docker-postgresql
- https://github.com/kibatic/docker-single-node-hadoop/
- https://github.com/bbonnin/docker-hadoop-3/blob/master/Dockerfile