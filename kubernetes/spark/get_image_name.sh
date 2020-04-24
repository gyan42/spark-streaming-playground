#!/usr/bin/env bash

# run this script after running make, otherwise it will fail
./bin/kubectl get svc registry-docker-registry -o=jsonpath='{.spec.clusterIP}':5000/$1