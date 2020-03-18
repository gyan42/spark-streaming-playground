### Scalable REST end point

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

![](images/ner_out.png)