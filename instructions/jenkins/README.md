# Jenkins deployment

### 1) Deploy Jenkins with HELM

* Add Charts to HELM:

  ```
  helm repo add jenkins https://charts.jenkins.io
  helm repo update
  ```
* Deploy Jenkins with HELM into Kind K8s cluster with following command:

  ```
  helm upgrade --install jenkins jenkins/jenkins -n jenkins
  ```
* Change port type to NodePort with command: .

  ```
  kubectl patch svc jenkins -n jenkins -p '{"spec": {"type": "NodePort"}}'
  ```
* To access to server, use following command:

  ```
  kubectl port-forward service/jenkins 8080:8080 -n jenkins
  ```
* Open the Browser and enter to server (take IP address from IP that you get after port-forward):

  ```
  http://<IP-address or server-name>:8080
  ```

### 2) Configuration of Jenkins

* Open another terminal, write this command to discover first password:

  ```
  `exec --namespace jenkins -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/chart-admin-password && echo.
  ```
* Enter into jenkins pod:

  ```
  kubectl exec -it `<jenkins-pod-name>` -- /bin/bash
  ```
* Go to home page with command: ``cd ~``:

  ```
  cd ~
  ```
* Download following Jenkins CLI jar file: .

  ```
  `curl -O http://<IP-address or server-name>:8080/jnlpJars/jenkins-cli.jar`
  ```
* Install the next plugins with followind command:

```
java -jar jenkins-cli.jar -s http://<IP-address or server-name>:8080/ -auth <user>:<api-token> install-plugin \
kubernetes:3937.vd7b_82db_e347b_ \
workflow-aggregator:596.v8c21c963d92d \
git:5.2.0 \
configuration-as-code:1647.ve39ca_b_829b_42 \
gitlab-plugin:1.7.14 \
blueocean:1.27.4 \
workflow-multibranch:756.v891d88f2cd46 \
login-theme:46.v36f624efb_23d \
prometheus:2.2.3 \
github-oauth:588.vf696a_350572a_java -jar jenkins-cli.jar -s http://localhost:8080/ -auth <user>:<api-token> install-plugin kubernetes:3937.vd7b_82db_e347b_ workflow-aggregator:596.v8c21c963d92d git:5.2.0 configuration-as-code:1647.ve39ca_b_829b_42 gitlab-plugin:1.7.14 blueocean:1.27.4 workflow-multibranch:756.v891d88f2cd46 login-theme:46.v36f624efb_23d prometheus:2.2.3 github-oauth:588.vf696a_350572a_ github:1.39.0 prometheus:773.v3b_62d8178eec pipeline-stage-view:2.33
  
```

* After installation of plugins, restart the plugin:
  ```
  java -jar jenkins-cli.jar -s http://<IP-address or server-name>:8080/ -auth <user>:<api-token> safe-restart
  ```

### 3) Add Credentials to Jenkins

* Go to Settings -> Security -> Credentials -> Domains -> + Add Credentials
* Add credentials that connects to GitHub (username/password (using token from GitHub)).
* Add credentials that connects to DockerHub (username/password (using token from Docker Hub)).
* Add additional credentials that connects to GitHub (secret text) - Using token from GitHub.

### 4) Add Multibranch-Pipeline

* Go to + New Item -> Multibranch Pipeline -> Choosing name -> OK.
* In Branch Sources in the settings, choose GitHub repository and credentials to GitHub that you created (username/password).
* In Build Configuration choose By Jenkinsfile with path Jenkinsfile.
* In Property strategy choose All branches get the same properties.
* In Scan Repository Triggers, Enable periodaclly if not run for 1 minute.
* Click Apply.
* Verify that pipeline works correctly.
