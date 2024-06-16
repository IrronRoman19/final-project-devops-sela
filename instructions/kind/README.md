# Kind K8s cluster deployment:

### 1) Install Docker Desktop

* If you using Windows OS in your computer, enable virtualization on your computer.
* If you using Windows OS in your computer, install WSL2 with following instructions: [Click Here](https://learn.microsoft.com/en-us/windows/wsl/install#install-wsl-command).
* Download and Install Docker Desktop from official page: [Click Here](https://www.docker.com/products/docker-desktop/).
* After installation of Docker Desktop, go to settings and Enable Kubernetes.

### 2) Install Kind K8s

* Download and Install Kind K8s from their official page with following instructions: [Click Here](https://kind.sigs.k8s.io/docs/user/quick-start/).
* After you downloaded Kind K8s check Kind version: ``kind version``.

### 3) Create cluster and create namespaces

* Create new Kind cluster:

  ```
  kind create cluster <CLUSTER_NAME>
  ```
* Check created cluster:

  ```
  kind get clusters
  ```
* Create namespaces "argocd", "jenkins" and "observation":

  ```
  kubectl create namespace <choose-namespace>
  ```
* Check created namespace: 

  ```
  kubectl get namespaces
  ```
