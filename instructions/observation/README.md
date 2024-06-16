# Jenkins and Grafana deployment

## 1) Prometheus

### 1.1) Deploy Prometheus with HELM

* Add Prometheus repository into the chart:

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

* Deploy Prometheus with HELM into Kind K8s cluster with following command:

```
helm install prometheus prometheus-community/prometheus -n observation
```

* Change the Prometheus server service type to NodePort:

```
kubectl patch svc prometheus-server -n observation -p '{"spec": {"type": "NodePort"}}'
```

* Change the ArgoCD server to port 9090:

```
kubectl patch svc prometheus-server -n observation --type='json' -p='[{"op": "replace", "path": "/spec/ports/0/port", "value": 9090}]'
```

### 1.2) Access to Prometheus server

* To access to server, use following command:

```
kubectl port-forward service/prometheus-server 9090:9090 -n observation
```

* Open the Browser and enter to server (take IP address from IP that you get after port-forward):

```
http://<IP-address or server-name>:9090
```

## 2) Grafana

### 2.1) Deploy Grafana with HELM

* Add Grafana repository into the chart:

```
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

* Deploy Grafana with HELM into Kind K8s cluster with following command:

```
helm install grafana grafana/grafana -n observation
```

* Change the Grafana server service type to NodePort:

```
kubectl patch svc grafana -n observation -p '{"spec": {"type": "NodePort"}}'
```

* Change the ArgoCD server to port 3000:

```
kubectl patch svc grafana -n observation --type='json' -p='[{"op": "replace", "path": "/spec/ports/0/port", "value": 3000}]'
```

* We can find the username and password required to log in into Grafana using the following commands. It will show the values in encrypted format, which we can decode using OpenSSL and base 64 formats. (recomended to use GIT bash CLI).

```
kubectl get secret -n observation grafana -o yaml
echo “password_value” | openssl base64 -d ; echo
echo “username_value” | openssl base64 -d ; echo
```

### 2.2) Access to Grafana server

* To access to server, use following command:

```
kubectl port-forward service/grafana 3000:3000 -n observation
```

* Open the Browser and enter to server (take IP address from IP that you get after port-forward):

```
http://<IP-address or server-name>:3000
```

### 3) Metrics:

* Sign in in Grafana server with admin user and password that you got above.
* Connect into Prometheus server that you deployed.
* Create new dashboard and Then new visualisation

1) 1st visualisation will shows CPU usage of application pods with following query:
   ```
   sum(rate(container_cpu_usage_seconds_total{namespace="default", pod=~"task-app-.*|task-db-.*"}[5m])) by (pod) * 1000
   ```
2) 2nd visualisation will shows Memory usage of application pods with following query:
   ```
   sum(container_memory_usage_bytes{namespace="default", pod=~"task-app-.*|task-db-.*"}) by (pod) 
   / 1024 / 1024
   ```

* After you finished you will save the visualisation and then save dashboard.
