# Task Application deployment (includes MongoDB database)

### 1) Install HELM

* Download and install Helm with following instructions [Click here](https://helm.sh/docs/intro/install/).
* Check helm version:
  ```
  helm version
  ```

### 2) Package application into the HELM

* Open the terminal, clone the repository to local machine to your path directory:

  ```
  git clone https://github.com/IrronRoman19/final-project-devops-sela
  ```
* Package the app with following command:

  ```
  helm package ./helm/task-app
  ```
* Deploy the app into Kind K8s cluster with following command:

  ```
  helm install task-app <PACKAGE_NAME>
  ```
* To access to app, use following command:

  ```
  kubectl port-forward service/task-app 5000:5000
  ```
* Open another terminal, To access to database, use following command:

  ```
  `kubectl port-forward service/task-db 27017:27017
  ```

### 3) Get access to the WEB and MongoDB

* Open the Browser and enter to App (take IP address from IP that you get after port-forward).
  ```
  http://<IP-address or server-name>:8080
  ```
* Download and Install MongoDB Compass: [Click Here](https://www.mongodb.com/docs/compass/current/install/).
* Use MongoDB Compass to access to database in following link: (take IP address from IP that you get after port-forward).
  ```
  mongodb://<MONGO_USER>:<MONGO_PASSWORD>@<IP_ADDRESS>:27017/
  ```
