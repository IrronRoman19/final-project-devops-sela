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
        MONGO_DB_HOST = 'mongodb.jenkins.svc.cluster.local'
        MONGO_DB_PORT = '27017'
    }

    stages {
        stage('Setup') {
            steps {
                checkout scm
                script {
                    // Initialize environment
                    def initEnv = { echo 'Environment setup initialized' }
                    def getUniqueBuildIdentifier = { suffix = '' -> System.currentTimeMillis().toString() + (suffix ? '-' + suffix : '') }
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

        stage('Run Unit Tests') {
            steps {
                script {
                    dockerImage.inside("--network=host") {
                        // Start MongoDB for testing
                        sh 'docker run -d --name mongo_test -e MONGO_INITDB_ROOT_USERNAME=mongoadmin -e MONGO_INITDB_ROOT_PASSWORD=secret -p 27018:27017 mongo:4.4'

                        // Wait for MongoDB to be ready
                        sh '''
                        until python -c "import sys; from pymongo import MongoClient; client = MongoClient('localhost', 27018); sys.exit(0 if client.admin.command('ping')['ok'] == 1 else 1)"
                        do
                        echo "Waiting for test MongoDB connection at localhost:27018..."
                        sleep 5
                        done
                        echo "Test MongoDB is up and running at localhost:27018"
                        '''

                        // Set environment variables for the test
                        withEnv(["MONGO_DB_HOST=localhost", "MONGO_DB_PORT=27018", "MONGO_DB_NAME=task_db_test"]) {
                            // Run the tests
                            sh 'pytest ./app'
                        }

                        // Cleanup
                        sh 'docker stop mongo_test'
                        sh 'docker rm mongo_test'
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
    }
}
