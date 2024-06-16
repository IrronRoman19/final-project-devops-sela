# ArgoCD Deployment

### 1) Deploy ArgoCD with HELM

* Deploy ArgoCD with HELM into Kind K8s cluster with following command:

```
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

* Change the ArgoCD server service type to NodePort:

```
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```

* Change the ArgoCD server to port 8089:

```
kubectl patch svc argocd-server -n argocd --type='json' -p='[{"op": "replace", "path": "/spec/ports/0/port", "value": 8089}]'
```

### 2) Access to ArgoCD server

* For getting password, use following command (recommended using GIT bash CLI):

```
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d
```

* To access to server, use following command:

```
kubectl port-forward service/argocd-server 8089:8089 -n argocd
```

* Open the Browser and enter to server (take IP address from IP that you get after port-forward):

```
http://<IP-address or server-name>:8089
```

### 3) Install App sync and image updater

* Install ArgoCD image updater:

  ```
  helm install argocd-image-updater argo/argocd-image-updater -n argocd --set argoCD.namespace=argocd
  ```
* Use argo-app.yaml to deploy app sync:

  ```
  apiVersion: argoproj.io/v1alpha1
  kind: Application
  metadata:
    name: cd-task-app
    namespace: argocd
    annotations:
      argocd-image-updater.argoproj.io/image-list: irronroman19/task-app
      argocd-image-updater.argoproj.io/write-back-method: argocd
      argocd-image-updater.argoproj.io/update-strategy: latest
  spec:
    project: default
    source:
      repoURL: 'https://github.com/IrronRoman19/final-project-devops-sela'
      targetRevision: main
      path: helm/task-app
    destination:
      server: 'https://kubernetes.default.svc'
      namespace: default
    syncPolicy:
      automated:
        prune: true
        selfHeal: true
        allowEmpty: true
  ```
* Use argo-image-updater.yaml to update config for image updater:

  ```
  apiVersion: v1
  kind: ConfigMap
  metadata:
    name: argocd-image-updater-config
    namespace: argocd
  data:
    registries.conf: |
      registries:
        - name: Docker Hub
          api_url: https://index.docker.io/v1/
          ping: true
          credentials: null
    config.yaml: |
      log.level: info
      image-updaters:
        - match: '*'
          notify: true
          strategy: latest
          interval: 1m

  ```
* Apply 2 above yaml files:

  ```
  kubectl apply -f <your-path>/argo-app.yaml -n argocd
  kubectl apply -f <your-path>/argo-image-updater.yaml -n argocd
  ```
