# Kubernetes
Some common commands that are handy while working with kubernetes.

```shell script
# starts the pods in yor machine
sudo minikube start --vm-driver=none 
sudo minikube stop

# list down all the pods 
kubectl get pods
# list all 
kubectl get all
# delete services
kubectl delete ${name from above list}
# eg:
kubectl delete deployment.apps/spacy-flask-ner-python

 
```

## Setting up with our docker image

```
sudo minikube start --vm-driver=none 

# note only first time below commands will add the docker file and run its as as service,
# there on, our service will be started by default when we start the Kubernetes!

kubectl create -f kubernetes/spacy-flask-ner-python.deployment.yaml 
kubectl create -f kubernetes/spacy-flask-ner-python.service.yaml
# on a seprate terminal
curl -i -H "Content-Type: application/json" -X POST -d '{"text":"Ram read a book on Friday 20/11/2019"}' http://127.0.0.1:30123/spacy/api/v0.1/ner

# kubernetes restart
kubectl delete service/spacy-flask-ner-python-service deployment.apps/spacy-flask-ner-python-deployment
# and then create the services again
```
 
## SE
### References
- https://medium.com/faun/how-to-restart-kubernetes-pod-7c702ca984c1