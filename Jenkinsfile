pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "irronroman19/task-app:latest"
        // EMAIL_RECIPIENTS = "email@example.com"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    docker.build(DOCKER_IMAGE)
                }
            }
        }

        stage('Unit Tests') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pytest app/tests'
            }
        }

        stage('HELM Package Build') {
            steps {
                sh 'helm package helm/task-app'
            }
        }

        stage('Push to DockerHub') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials-id') {
                        docker.image(DOCKER_IMAGE).push()
                    }
                }
            }
        }

        stage('Release Actions') {
            when {
                branch 'main'
            }
            steps {
                echo "Performing release actions..."
                // Add your release steps here
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        // failure {
        //     mail to: "${EMAIL_RECIPIENTS}",
        //          subject: "Failed Pipeline: ${currentBuild.fullDisplayName}",
        //          body: "Something is wrong with ${env.BRANCH_NAME} branch. Check Jenkins for details."
        // }
        // success {
        //     script {
        //         if (currentBuild.previousBuild != null && currentBuild.previousBuild.result == 'FAILURE') {
        //             mail to: "${EMAIL_RECIPIENTS}",
        //                  subject: "Recovered Pipeline: ${currentBuild.fullDisplayName}",
        //                  body: "The build for ${env.BRANCH_NAME} has recovered from the previous failure."
        //         }
        //     }
        // }
    }
}