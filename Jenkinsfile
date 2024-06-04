def dockerImage
pipeline {
    agent {
        kubernetes {
            label 'jenkins-agent-pod'
            idleMinutes 1
            yamlFile 'build-pod.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '1'))
    }

    environment {
        DOCKER_IMAGE = 'irronroman19/task-app'
        DOCKER_CREDENTIALS_ID = 'docker-token'
        GITHUB_REPO = 'IrronRoman19/final-project-devops-sela'
    }

    stages {
        stage('Setup') {
            steps {
                checkout scm
                script {
                    def initEnv = {
                        echo 'Environment setup initialized'
                    }

                    def getUniqueBuildIdentifier = { suffix = '' ->
                        return System.currentTimeMillis().toString() + (suffix ? '-' + suffix : '')
                    }

                    initEnv()

                    def id = getUniqueBuildIdentifier()
                    if (env.BRANCH_NAME == 'main') {
                        env.BUILD_ID = "1." + id
                    } else {
                        def issueNumber = "issueNumber"
                        env.BUILD_ID = "0." + getUniqueBuildIdentifier(issueNumber) + "." + id
                    }
                    currentBuild.displayName += " {build-name:" + env.BUILD_ID + "}"
                }
            }
        }

        stage('Clone Repository') {
            steps {
                git branch: env.BRANCH_NAME, url: "https://github.com/${env.GITHUB_REPO}.git"
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${DOCKER_IMAGE}:${env.BUILD_ID}", "./app")
                }
            }
        }

        stage('Deploy to Kind') {
            steps {
                script {
                    sh 'kind create cluster --name jenkins-cluster || echo "Cluster already exists"'
                    sh 'helm install task-app ./helm/task-app --wait'
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    dockerImage.inside {
                        sh 'pytest ./app/test'
                    }
                }
            }
        }

        stage('Build Helm Package') {
            steps {
                sh 'helm package ./helm/task-app'
            }
        }

        stage('Push Docker Image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', env.DOCKER_CREDENTIALS_ID) {
                        dockerImage.push("${env.BRANCH_NAME}-${env.BUILD_ID}")
                        dockerImage.push('latest')
                    }
                }
            }
        }

        stage('Push Helm Package') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh "helm push ./helm/task-app"
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    sh 'helm uninstall task-app'
                    sh 'kind delete cluster --name jenkins-cluster'
                }
            }
        }
    }
}
