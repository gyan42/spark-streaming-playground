# Spark on K8s

[Google has adopted Kubernetes as cluster manager](https://thenewstack.io/big-data-google-replaces-yarn-with-kubernetes-to-schedule-apache-spark/),
 so even our client wanted to test out Kubernetes for Spark Applications

------------------------------------------------------------------------------------------------------------------------

## Requirements
Setup local Kubernetes cluster to run Spark examples

------------------------------------------------------------------------------------------------------------------------

## Implementation

Read the Spark [Kubernetes docs](https://spark.apache.org/docs/latest/running-on-kubernetes.html).

- [Spark Setup](https://gyan42.github.io/spark-streaming-playground/build/html/setup/ApacheSpark.html)
- [Kubernetes](https://gyan42.github.io/spark-streaming-playground/build/html/setup/Kubernetes.html)

Make sure the Spark version > 2.4.5 for this to work seamlessly.

Handy Links
- [https://docs.docker.com/registry/insecure/](https://docs.docker.com/registry/insecure/)

A [MakeFile](https://github.com/gyan42/spark-streaming-playground/tree/master/kubernetes/spark) was put in place to download all needed binaries, prepare the docker image with respect to Spark and use
the Spark image to run the example locally

```shell script
cd /path/to/spark-streaming-playground/kubernetes/spark/
```

Install k8s tooling locally, start minikube, initialize helm and deploy a docker registry chart to your minikube:
```
make
```

If everything goes well, you should see a message like this: Registry successfully deployed in minikube. Make sure you 
add 192.168.99.100:30000 to your insecure registries before continuing.
Check https://docs.docker.com/registry/insecure/ for more information on how to do it in your platform.

In simple words, you needs to add an entry as follows:
```
sudo vim /etc/docker/daemon.json # and add followning line
  {
    "insecure-registries" : ["192.168.99.100:30000"]
  } 
```

Restart the docker...
```
sudo systemctl daemon-reload
sudo systemctl restart docker
docker info
```

You should see following log:
```
    Insecure Registries:
     192.168.99.100:30000
     127.0.0.0/8
```

Push the spark images to our private docker registry
```
make docker-push
```

HINT: if you see "Get https://192.168.99.100:30000/v2/: http: server gave HTTP response to HTTPS client" 
go back and check whether you have it listed in your insecure registries


Once your images are pushed, let's run a sample spark job (first on client mode):
```
$SPARK_HOME/bin/spark-submit \
    --master k8s://https://$(minikube ip):8443 \
    --deploy-mode client \
    --conf spark.kubernetes.container.image=$(./get_image_name.sh spark) \
    --class org.apache.spark.examples.SparkPi \
    $SPARK_HOME/examples/jars/spark-examples_2.11-2.4.5.jar
```

------------------------------------------------------------------------------------------------------------------------

## Limitations / TODOs
- Explore more on the Kubernetes driver options
- Explore how to run the example on AWS


**References**
- https://tech.olx.com/running-spark-on-kubernetes-a-fully-functional-example-and-why-it-makes-sense-for-olx-d56b6a61fcbe
- https://github.com/olx-global/spark-on-k8s