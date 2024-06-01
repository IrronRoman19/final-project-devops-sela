pipeline {
    agent any

    environment {
        DOCKER_CREDENTIALS_ID = 'docker-token'
        DOCKER_IMAGE = 'irronroman19/task-app'
        // EMAIL_RECIPIENTS = 'project-managers@example.com'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: '${BRANCH_NAME}', url: 'https://github.com/IrronRoman19/final-project-devops-sela.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${env.BRANCH_NAME}")
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    docker.image("${DOCKER_IMAGE}:${env.BRANCH_NAME}").inside {
                        sh 'pytest tests/'
                    }
                }
            }
        }

        stage('Build HELM Package') {
            steps {
                sh 'helm package helm-chart/'
            }
        }

        stage('Push Docker Image (main branch only)') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry('', DOCKER_CREDENTIALS_ID) {
                        docker.image("${DOCKER_IMAGE}:${env.BRANCH_NAME}").push("latest")
                    }
                }
            }
        }
    }

    // post {
    //     failure {
    //         mail to: "${EMAIL_RECIPIENTS}",
    //              subject: "Failed Pipeline: ${currentBuild.fullDisplayName}",
    //              body: "Something is wrong with ${env.BUILD_URL}"
    //     }

    //     success {
    //         script {
    //             if (currentBuild.previousBuild?.result == 'FAILURE') {
    //                 mail to: "${EMAIL_RECIPIENTS}",
    //                      subject: "Back to Normal: ${currentBuild.fullDisplayName}",
    //                      body: "The build is back to normal: ${env.BUILD_URL}"
    //             }
    //         }
    //     }
    // }
}
