pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'irronroman19/task-app'
        DOCKER_CREDENTIALS_ID = 'docker-token'
        GITHUB_REPO = 'IrronRoman19/final-project-devops-sela'
    }
    stages {
        stage('Clone Repository') {
            steps {
                git branch: env.BRANCH_NAME, url: "https://github.com/${env.GITHUB_REPO}.git"
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    dockerImage = docker.build("${env.DOCKER_IMAGE}:latest")
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
                    docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_CREDENTIALS_ID) {
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
                    sh 'helm push ./helm/task-app --username $DOCKERHUB_USERNAME --password $DOCKERHUB_PASSWORD'
                }
            }
        }
    }
}
