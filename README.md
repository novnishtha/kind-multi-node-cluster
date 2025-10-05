# Multi-Node Spark Cluster using KIND (Kubernetes in Docker)
This repository contains the necessary configuration and code to run an Apache Spark application in cluster deployment mode on a local, multi-node Kubernetes cluster created with Kind.

---

## Features
- PySpark job packaged in a Docker image
- Sample data under `data_skew/` baked into the image 
- Kubernetes Job manifests for:
  - Static executors (`static-job-spark.yaml`)
  - Dynamic allocation (`spark-dynamic-job.yaml`)
  - Dynamic allocation with AQE disabled (`spark-notaqe.yaml`)
- Kind cluster config and RBAC setup


## Prerequisites
Ensure you have the following installed on your system:

- **Kind**: A tool for running Kubernetes in Docker.
- **kubectl**: The Kubernetes command-line tool.
- **Docker Desktop**: The containerization platform.
- ~4GB free RAM

## Project Directory

``` 
/docker_transactions
├── transformations.py         <-- PySpark script
├── requirements.txt           <-- Lists Python dependencies (pyspark)
├── Dockerfile                 <-- Blueprint for Docker image (includes the USER root)
├── kind-config.yaml           <-- Defines the multi-node cluster topology
├── rbac.yaml                  <-- Defines the Spark ServiceAccount permissions
├── spark-dynamic-job.yaml     <-- Defines the Kubernetes Job (dynamic allocation)
├── spark-notaqe.yaml          <-- Kubernetes Job (dynamic allocation with AQE disabled)
├── static-job-spark.yaml      <-- Kubernetes Job (static allocation)
└── data_skew/                 <-- Contains the data files
    ├── customers.parquet
    └── transactions.parquet
```

## Build the Docker Image
```
docker build -t pyspark-jobs:latest .
```

## Run on a Local Kind Cluster
1) Create a Kind cluster:
```
kind create cluster --config kind-config.yaml
```

2) Create ServiceAccount and RBAC (used by Spark driver):
```
kubectl apply -f rbac.yaml
```

3) Load the image into the Kind cluster (imagePullPolicy is `Never`):
```
kind load docker-image pyspark-jobs:latest
```

4) Submit a Spark job (choose any ONE of the following at a time):
- Static executors:
  ```
  kubectl apply -f static-job-spark.yaml
  ```
- Dynamic allocation:
  ```
  kubectl apply -f spark-dynamic-job.yaml
  ```
- Dynamic allocation, AQE disabled:
  ```
  kubectl apply -f spark-notaqe.yaml
  ```

5) Monitor status and logs:
```
kubectl get jobs
kubectl logs job/spark-static-job -f             # if you applied static-job-spark.yaml
kubectl logs job/spark-dynamic-job -f            # if you applied spark-dynamic-job.yaml
kubectl logs job/spark-notaqe-job -f             # if you applied spark-notaqe.yaml
```

Check driver or executor logs individually.
```
kubectl logs <driver-pod-name>
kubectl logs <executor-pod-name>
```

Use the watch command to see the pods transition from Pending to Running. This verifies that the scheduler is placing executors on different nodes.
```
kubectl get pods -o wide --watch
```

## Spark UI 
To allow Spark UI inspection, sleep() command has been used. To reach the driver UI (default 4040), port-forward the driver pod.
```
kubectl get pods -o wide
kubectl port-forward <driver-pod-name> 4040:4040
```
Then open http://localhost:4040 in your browser.


## Configuration
- Edit `static-job-spark.yaml` to change the number of executors and resources.
- Edit `spark-dynamic-job.yaml` to tune min/max executors and dynamic allocation.
- Edit `spark-notaqe.yaml` to experiment with execution behavior with AQE disabled.
- In all manifests, adjust executor cores/memory as needed:
  - `spark.executor.instances`, `spark.executor.cores`, `spark.executor.memory`
  - For dynamic allocation: `spark.dynamicAllocation.*`
- Also can set any types of configurations in these manifests itself.

## Cleanup
```
kubectl delete -f static-job-spark.yaml || true
kubectl delete -f spark-dynamic-job.yaml || true
kubectl delete -f spark-notaqe.yaml || true
kubectl delete all --all #to delete all resources(jobs, pods) all together at the same time

kind delete cluster
```

## Notes
- The base image is `spark:latest` and Python dependencies are installed from `requirements.txt`.
- If you want to run the script locally (outside containers), update the file paths in `transformations.py` or ensure the data is available under `/app/data_skew/` via a bind mount.
