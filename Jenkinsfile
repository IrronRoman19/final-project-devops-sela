@Library('EZJEL/feature') _

def dockerImage
pipeline {
    agent {
        kubernetes {
            label 'docker-image-deploy'
            idleMinutes 5
            yamlFile './build-pod.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    environment {
        DOCKER_IMAGE = 'irronroman19/task-app'
        DOCKER_CREDENTIALS_ID = 'docker-token'
        GITHUB_REPO = 'IrronRoman19/final-project-devops-sela'
        // DOCKERHUB_USERNAME = credentials('dockerhub-username')
        // DOCKERHUB_PASSWORD = credentials('dockerhub-password')
    }

    stages {
        stage('Setup') {
            steps {
                checkout scm
                script {
                    ezEnvSetup.initEnv()
                    def id = ezUtils.getUniqueBuildIdentifier()
                    if(env.BRANCH_NAME == 'main') {
                        env.BUILD_ID = "1." + id
                    } else {
                        env.BUILD_ID = "0." + ezUtils.getUniqueBuildIdentifier("issueNumber") + "." + id
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
                    dockerImage = docker.build("${DOCKER_IMAGE}:${env.BUILD_ID}")
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh 'pytest app'
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
                    // sh "helm push ./helm/task-app --username $DOCKERHUB_USERNAME --password $DOCKERHUB_PASSWORD"
                    sh "helm push ./helm/task-app"
                }
            }
        }
    }
}
