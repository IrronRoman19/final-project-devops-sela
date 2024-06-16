# DevOps Final Project - Task Application

Final Project within the Sela DevOps course. This project summarizes material that learned throughout the course. Current Project includes application itself, infrastructure and pipelines.

### Application

Task Application allows you to get tasks from database, you can complete or uncomplete the tasks. Also you can create, edit, remove tasks.

Task Application developed with python code with using Flask application. WEB pages developed with HTML and CSS.  Application connects to MongoDB database that keeps tasks. Also, this app packaging into Dockerfile image and HELM package.

In addition, for using CI pipeline in Jenkins, after building image, checking with additional python application with using Pytest that tests functionality of the app without affecting with database data that contains existing data.

Most importantly in the app, when deploying to K8s cluster with Helm, you can see that application contains two pods: task-app and task-db. I want to certain you even if you delete the task-app or task-db pod, data will be saved because data saved in MongoDB volume.

### Infrastructure

All of Infrastracture that you will find out below, works in Kind K8s cluster that works locally in local machine and contains namespaces: default, jenkins, argocd and observation.

##### Default namespace

Task Application with MongoDB database which I said above. Task application works in port 5000 (with using type NodePort) and MongoDB database works in port 27017 (with using type NodePort).

##### Jenkins namespace

Jenkins server responsibles for CI processes and running CI pipelines (feature, main). Also, in Jenkins server have installed plugins:

* kubernetes:3937.vd7b_82db_e347b_
* workflow-aggregator:596.v8c21c963d92d
* git:5.2.0
* configuration-as-code:1647.ve39ca_b_829b_42
* gitlab-plugin:1.7.14
* blueocean:1.27.4
* workflow-multibranch:756.v891d88f2cd46
* login-theme:46.v36f624efb_23d
* prometheus:2.2.3
* github-oauth:588.vf696a_350572a_
* github:1.39.0
* prometheus:773.v3b_62d8178eec
* pipeline-stage-view:2.33

In addition, Jenkins server connected to GitHub repository and Docker Hub image. Jenkins server works in port 8080 (with using type NodePort).

##### Argocd namespace

ArgoCD server responsibles for CD process and deploying the updated app. Also, ArgoCD connected to GitHub repository and Docker Hub image. ArgoCD server works in port 8089 (with using type NodePort).

##### Observation namespace

Prometheus server responsibles for observation metrics from application pods. In this project using metrics to observe CPU usage and Memory usage in app pods. Prometheus server works in port 9090 (with using type NodePort).

Grafana server imports the above metrics from Prometheus servers relevant metrics. Grafana server works in port 3000 (with using type NodePort).

### Pipelines

There have CI/CD pipelines that work in Jenskins with using CI multibranch pipeline (feature and main branches) with using Jenkinsfile and Argocd CD pipeline.

##### CI Feature Pipeline:

* Checks every minute if github repository (feature branch) have changed.
* Step 1 - Setup build.
* Step 2 - Clone repository from GitHub project repository.
* Step 3 - Build Docker image.
* Step 4 - Run Unit tests with using pytest.
* Step 5 - Package app into HELM package.
* Step 6 - Create pull request to merge into main branch
* Step 7 - Approve the request manually.
* Step 8 - Merge feature branch with main branch

##### CI Main Pipeline:

* Step 1 - Setup build.
* Step 2 - Clone repository from GitHub project repository.
* Step 3 - Build Docker image.
* Step 4 - Run Unit tests with using pytest.
* Step 5 - Package app into HELM package.
* Step 6 - Push 2 Docker images into DockerHub repository (latest and build number).

##### CD Pipeline:

* When latest Docker Image have changed, Application will synchronized.
* After sync app, it will automaticly install new task-app pod and terminates old task-app pod.

## Instructions:

1. Deploy Kind K8s cluster: [Instructions](./instructions/kind/README.md).
2. Deploy Python Task applicaiton + MongoDB database: [Instructions](./instructions/task-app/README.md).
3. Deploy Jenkins: [Instructions](./instructions/jenkins/README.md).
4. Deploy ArgoCD: [Instructions](./instructions/argocd/README.md).
5. Deploy Monitoring (Prometheus + Grafana): [Instructions](./instructions/observation/README.md).
