K8S_VERSION ?= v1.15.4
HELM_VERSION ?= v2.14.2
MINIKUBE_VERSION ?= latest
MINIKUBE_VMDRIVER ?= virtualbox
NUM_CPUS = 8

OS ?= $(shell uname -s | tr '[:upper:]' '[:lower:]')
ARCH ?= amd64

.PHONY: all
all: k8s-tooling start-minikube helm-init start-registry

#################
## k8s tooling ##
#################

bin/kubectl:
	mkdir -p bin/
	curl --progress-bar -Lo bin/kubectl https://storage.googleapis.com/kubernetes-release/release/$(K8S_VERSION)/bin/$(OS)/$(ARCH)/kubectl
	chmod +x bin/kubectl

tmp/helm:
	mkdir -p tmp/
	curl --progress-bar -Lo tmp/helm.tar.gz https://get.helm.sh/helm-$(HELM_VERSION)-$(OS)-$(ARCH).tar.gz
	tar xvzf tmp/helm.tar.gz
	mv $(OS)-$(ARCH) tmp/helm
	rm -f tmp/helm.tar.gz

bin/helm: tmp/helm
	cp -a tmp/helm/helm bin/helm
	chmod +x bin/helm

bin/tiller: tmp/helm
	cp -a tmp/helm/tiller bin/tiller
	chmod +x bin/tiller

bin/minikube:
	curl --progress-bar -Lo bin/minikube https://storage.googleapis.com/minikube/releases/$(MINIKUBE_VERSION)/minikube-$(OS)-$(ARCH)
	chmod +x bin/minikube

.PHONY: helm-init
helm-init: bin/helm bin/tiller
	./bin/helm init --wait

.PHONY: k8s-tooling
k8s-tooling: bin/kubectl bin/helm bin/tiller bin/minikube

##############
## Minikube ##
##############

.PHONY: start-minikube
start-minikube: bin/minikube
	./bin/minikube start --cpus=$(NUM_CPUS) --memory=4000mb --vm-driver=$(MINIKUBE_VMDRIVER) --kubernetes-version=$(K8S_VERSION)

.PHONY: stop-minikube
stop-minikube: bin/minikube
	./bin/minikube stop

#####################
## Docker registry ##
#####################

.PHONY: start-registry
start-registry:
	./bin/helm upgrade --install --wait registry -f registry-values.yaml stable/docker-registry
	echo "Registry successfully deployed in minikube. Make sure you add $(shell minikube ip):30000 to your insecure registries before continuing. Check https://docs.docker.com/registry/insecure/ for more information on how to do it in your platform."

.PHONY: stop-registry
stop-registry:
	./bin/helm delete --purge registry

###############################################################################
##                   Spark docker image building                             ##
## see: https://github.com/apache/spark/blob/master/bin/docker-image-tool.sh ##
###############################################################################

.PHONY: docker-build
docker-build:
	cd $(SPARK_HOME) && ./bin/docker-image-tool.sh -r $(shell minikube ip):30000 -t latest build

.PHONY: docker-push
docker-push:
	cd $(SPARK_HOME) && ./bin/docker-image-tool.sh -r $(shell minikube ip):30000 -t latest push

.PHONY: clean
clean:
	echo "Make sure you remove $(shell minikube ip):30000 from your list of insecure registries."
	./bin/minikube delete
	rm -rf tmp/* bin/*
