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
        GITHUB_USERNAME = 'irronroman19'
        GITHUB_TOKEN = credentials('git-secret')
        MONGO_DB_HOST = 'task-db.default.svc.cluster.local'
        MONGO_DB_PORT = '27017'
    }

    stages {
        stage('Setup') {
            steps {
                checkout scm
                script {
                    def initEnv = { echo 'Environment setup initialized' }
                    def getUniqueBuildIdentifier = { suffix = '' -> System.currentTimeMillis().toString() + (suffix ? '-' + suffix : '') }
                    initEnv()
                    def id = getUniqueBuildIdentifier()
                    if (env.BRANCH_NAME == 'main') {
                        env.BUILD_ID = "1." + id
                    } else {
                        env.BUILD_ID = "0." + getUniqueBuildIdentifier('feature') + "." + id
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
                    dockerImage.inside {
                        sh 'pytest ./app'
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

        stage('Create Pull Request') {
            when {
                branch 'feature'
            }
            steps {
                script {
                    withCredentials([string(credentialsId: 'git-secret', variable: 'GIT_TOKEN')]) {
                        def createPR = """
                            curl -u ${env.GIT_TOKEN} -X POST -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${env.GITHUB_REPO}/pulls -d '{
                                "title": "Auto PR from Jenkins: ${env.BUILD_ID}",
                                "head": "${env.BRANCH_NAME}",
                                "base": "main"
                            }'
                        """
                        sh createPR
                    }
                }
            }
        }

        stage('Manual Approval') {
            when {
                branch 'feature'
            }
            steps {
                script {
                    input message: 'Approve the merge to main?', ok: 'Approve'
                }
            }
        }

        stage('Update Pull Request Status') {
            when {
                branch 'feature'
            }
            steps {
                script {
                    def prList = sh(script: "curl -u ${env.GIT_TOKEN} -H \"Accept: application/vnd.github.v3+json\" https://api.github.com/repos/${env.GITHUB_REPO}/pulls?head=${env.GITHUB_USERNAME}:${env.BRANCH_NAME}", returnStdout: true).trim()
                    def prNumber = new groovy.json.JsonSlurper().parseText(prList).find { it.head.ref == "${env.BRANCH_NAME}" }.number
                    withCredentials([string(credentialsId: 'git-secret-approver', variable: 'APPROVER_GIT_TOKEN')]) {
                        def approvePR = """
                            curl -u ${env.APPROVER_GIT_TOKEN} -X POST -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${env.GITHUB_REPO}/pulls/${prNumber}/reviews -d '{
                                "body": "Approved by Jenkins",
                                "event": "APPROVE"
                            }'
                        """
                        sh approvePR
                    }
                }
            }
        }

        stage('Trigger Main Branch Build') {
            when {
                branch 'feature'
            }
            steps {
                script {
                    build(job: 'ci-task-app', parameters: [string(name: 'BRANCH_NAME', value: 'main')])
                }
            }
        }
    }
}
