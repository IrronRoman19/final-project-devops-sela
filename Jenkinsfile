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
        MONGO_DB_HOST = 'task-db.default.svc.cluster.local'
        MONGO_DB_PORT = '27017'
        GITHUB_TOKEN = credentials('github-token')
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

        stage('Request Merge to Main') {
            when {
                not {
                    branch 'main'
                }
            }
            steps {
                script {
                    def pr = createPullRequest()
                    echo "Created Pull Request #${pr.number}"
                    currentBuild.description = "PR #${pr.number}"
                }
            }
        }

        stage('Manual Approval') {
            when {
                not {
                    branch 'main'
                }
            }
            steps {
                input message: 'Approve Merge to Main?', ok: 'Merge'
            }
        }

        stage('Merge to Main') {
            when {
                not {
                    branch 'main'
                }
            }
            steps {
                script {
                    mergePullRequest()
                }
            }
        }

        stage('Trigger Main Branch Build') {
            when {
                not {
                    branch 'main'
                }
            }
            steps {
                build(job: env.JOB_NAME, parameters: [string(name: 'BRANCH_NAME', value: 'main')])
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}

def createPullRequest() {
    def response = httpRequest(
        acceptType: 'APPLICATION_JSON',
        contentType: 'APPLICATION_JSON',
        httpMode: 'POST',
        requestBody: """{
            "title": "Merge ${env.BRANCH_NAME} into main",
            "head": "${env.BRANCH_NAME}",
            "base": "main"
        }""",
        url: "https://api.github.com/repos/${env.GITHUB_REPO}/pulls",
        customHeaders: [
            [name: 'Authorization', value: "token ${env.GITHUB_TOKEN}"]
        ]
    )
    return new groovy.json.JsonSlurper().parseText(response.content)
}

def mergePullRequest() {
    def prNumber = currentBuild.description.split('#')[1]
    httpRequest(
        acceptType: 'APPLICATION_JSON',
        contentType: 'APPLICATION_JSON',
        httpMode: 'PUT',
        url: "https://api.github.com/repos/${env.GITHUB_REPO}/pulls/${prNumber}/merge",
        customHeaders: [
            [name: 'Authorization', value: "token ${env.GITHUB_TOKEN}"]
        ]
    )
}
