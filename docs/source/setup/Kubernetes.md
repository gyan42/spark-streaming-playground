# Kubernetes
Kubernetes is an open-source container-orchestration system for automating deployment, scaling and management of 
containerized applications.

Minikube is a tool that makes it easy to run Kubernetes locally. Minikube runs a single-node Kubernetes cluster 
inside a VM on your laptop for users looking to try out Kubernetes or develop with it day-to-day.

- [Architecture]((https://www.edureka.co/blog/kubernetes-architecture/))
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl-on-linux)
- [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)
- [Minikube Drivers](https://minikube.sigs.k8s.io/docs/drivers/)
    - [Docker](https://minikube.sigs.k8s.io/docs/drivers/docker/) 
    - [Hypervisor VirtualBox](https://www.virtualbox.org/wiki/Linux_Downloads)
        ```shell script
            sudo apt-get install libqt5opengl5
            sudo dpkg -i virtualbox-6.1_6.1.6-137129~Ubuntu~bionic_amd64.deb
        ```
- [Kubernetes YAML](https://www.mirantis.com/blog/introduction-to-yaml-creating-a-kubernetes-deployment/)
      

**Change owner and group**  
```
sudo chown -R $USER $HOME/.minikube
sudo chgrp -R $USER $HOME/.minikube
```

**Enable kubectl bash_completion**    
```
kubectl completion bash >>  ~/.bash_completion
. /etc/profile.d/bash_completion.sh
. ~/.bash_completion
```

[Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

Some common commands that are handy while working with kubernetes.

```shell script
# starts the pods in yor machine
# docker, virtualbox,
DRIVER = docker
minikube start --vm-driver=$(DRIVER) 
minikube stop


# list down all the pods 
kubectl get pods
# list all 
kubectl get all
# delete services
kubectl delete ${name from above list}
# eg:
kubectl delete deployment.apps/spacy-flask-ner-python

 
```

## API Quick Reference

Here’s a brief explanation of the various fields:

    replicas – Tells Kubernetes how many pods to create during a deployment. Modifying this field is an easy way to scale a containerized application.
    spec.strategy.type – Suppose there is another version of the application that needs to be deployed, and during the deployment phase, you need to update without facilitating an outage. The Rolling Update strategy allows Kubernetes to update a service without facilitating an outage by proceeding to update pods one at a time.
    spec.strategy.rollingUpdate.maxUnavailable – The maximum number of pods that can be unavailable during the Rolling update.
    spec.strategy.rollingUpdate.maxSurge – The maximum number of pods that can be scheduled above the desired number of pods.
    spec.minReadySeconds – An optional Integer that describes the minimum number of seconds, for which a new pod should be ready without any of its containers crashing for it to be considered available.
    spec.revisionHistoryLimit – An optional integer attribute that you can use to tell Kuberneres explicitly how many old ReplicaSets to retain at any given time.
    spec.template.metadata.labels – Adds labels to a deployment specification.
    spec.selector – An optional object that tells the Kubernetes deployment controller to only target pods that match the specified labels. Thus, to only target pods with the labels “app” and “deployer” you can make the following modification to our deployment yaml.


### References
- https://medium.com/faun/how-to-restart-kubernetes-pod-7c702ca984c1
- [https://medium.com/@yzhong.cs/getting-started-with-kubernetes-and-docker-with-minikube-b413d4deeb92](https://medium.com/@yzhong.cs/getting-started-with-kubernetes-and-docker-with-minikube-b413d4deeb92)
- [https://kubernetes.io/docs/concepts/services-networking/service/](https://kubernetes.io/docs/concepts/services-networking/service/)
- [https://kubernetes.io/docs/concepts/workloads/controllers/deployment/](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/)
- [https://intellipaat.com/blog/tutorial/devops-tutorial/kubernetes-cheat-sheet/](https://intellipaat.com/blog/tutorial/devops-tutorial/kubernetes-cheat-sheet/)