# PySpark Jobs on Kubernetes (Kind)

A minimal, containerized PySpark job with sample Parquet data and Kubernetes manifests for running on a local Kind cluster. It demonstrates both static executors and dynamic allocation, plus a variant with Adaptive Query Execution disabled for experimentation.

The core job in `transformations.py` reads Parquet datasets, performs several aggregations, prints timing metrics, and sleeps briefly so you can inspect the Spark UI.

---

## Features
- PySpark job packaged in a Docker image
- Sample data under `data_skew/` baked into the image
- Kubernetes Job manifests for:
  - Static executors (`static-job-spark.yaml`)
  - Dynamic allocation (`spark-dynamic-job.yaml`)
  - Dynamic allocation with AQE disabled (`spark-notaqe.yaml`)
- Kind cluster config and RBAC setup

## Repository Layout
```
.
├── Dockerfile
├── requirements.txt
├── transformations.py
├── data_skew/
│   ├── customers.parquet/
│   └── transactions.parquet/
├── kind-config.yaml
├── rbac.yaml
├── static-job-spark.yaml
├── spark-dynamic-job.yaml
└── spark-notaqe.yaml
```

## Prerequisites
- Docker (20+ recommended)
- kubectl
- kind
- ~4 GB free RAM

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

4) Submit a Spark job (choose ONE of the following):
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

## Spark UI (optional)
The job sleeps for a few minutes to allow Spark UI inspection. To reach the driver UI (default 4040), port-forward the driver pod. The exact labels may vary; try one of these approaches:
```
# Common label used by Spark on K8s
autopod=$(kubectl get pods -l spark-role=driver -o jsonpath='{.items[0].metadata.name}')
kubectl port-forward "$autopod" 4040:4040
```
If the label isn’t present, list pods and pick the driver (often ends with `-driver`):
```
kubectl get pods -o wide
kubectl port-forward <driver-pod-name> 4040:4040
```
Then open http://localhost:4040 in your browser.

## Run in Docker (no Kubernetes)
You can also run the job completely in Docker using the same image:
```
docker run --rm -p 4040:4040 pyspark-jobs:latest \
  /opt/spark/bin/spark-submit local:///app/transformations.py
```
Note: `transformations.py` reads data from `/app/data_skew/...` (inside the image), so running in Docker works out of the box.

## Configuration
- Edit `static-job-spark.yaml` to change the number of executors and resources.
- Edit `spark-dynamic-job.yaml` to tune min/max executors and dynamic allocation.
- Edit `spark-notaqe.yaml` to experiment with execution behavior with AQE disabled.
- In all manifests, adjust executor cores/memory as needed:
  - `spark.executor.instances`, `spark.executor.cores`, `spark.executor.memory`
  - For dynamic allocation: `spark.dynamicAllocation.*`

## Cleanup
```
kubectl delete -f static-job-spark.yaml || true
kubectl delete -f spark-dynamic-job.yaml || true
kubectl delete -f spark-notaqe.yaml || true
kind delete cluster
```

## Notes
- The base image is `spark:latest` and Python dependencies are installed from `requirements.txt`.
- If you want to run the script locally (outside containers), update the file paths in `transformations.py` or ensure the data is available under `/app/data_skew/` via a bind mount.

## License
Add your license file (e.g., MIT) to the repository root.
