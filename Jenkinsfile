pipeline {
    agent any
    environment {
        DOCKER_CREDENTIALS_ID = 'docker-token'
        GITHUB_CREDENTIALS_ID = 'git-token'
        DOCKER_IMAGE = 'irronroman19/task-app'
    }
    stages {
        // stage('Checkout') {
        //     steps {
        //         git branch: env.BRANCH_NAME, url: 'https://github.com/IrronRoman19/final-project-devops-sela'
        //     }
        // }
        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }
        stage('Unit Tests') {
            steps {
                script {
                    sh 'pytest'
                }
            }
        }
        stage('Build HELM Package') {
            steps {
                script {
                    sh 'helm package ./helm/task-app'
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
