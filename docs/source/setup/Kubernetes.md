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
      

**Change owner and group**
```
sudo chown -R $USER $HOME/.minikube
sudo chgrp -R $USER $HOME/.minikube
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
 

### References
- https://medium.com/faun/how-to-restart-kubernetes-pod-7c702ca984c1
- [https://medium.com/@yzhong.cs/getting-started-with-kubernetes-and-docker-with-minikube-b413d4deeb92](https://medium.com/@yzhong.cs/getting-started-with-kubernetes-and-docker-with-minikube-b413d4deeb92)
- [https://kubernetes.io/docs/concepts/services-networking/service/](https://kubernetes.io/docs/concepts/services-networking/service/)
- [https://kubernetes.io/docs/concepts/workloads/controllers/deployment/](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/)
- [https://intellipaat.com/blog/tutorial/devops-tutorial/kubernetes-cheat-sheet/](https://intellipaat.com/blog/tutorial/devops-tutorial/kubernetes-cheat-sheet/)