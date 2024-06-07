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
        GITHUB_CREDENTIALS_ID = 'git-token'
        GITHUB_USERNAME = 'irronroman19'
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
                    echo "Creating Pull Request from ${env.BRANCH_NAME} to main"
                    
                    def createPRPayload = """
                    {
                        "title": "Auto PR from Jenkins: ${env.BUILD_ID}",
                        "head": "${env.BRANCH_NAME}",
                        "base": "main"
                    }
                    """
                    echo "PR Payload: ${createPRPayload}"

                    def createPRResponse = sh(
                        script: """
                            curl -u ${env.GITHUB_USERNAME}:${env.GITHUB_CREDENTIALS_ID} -X POST -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${env.GITHUB_REPO}/pulls -d '${createPRPayload}'
                        """,
                        returnStdout: true
                    ).trim()

                    echo "Create PR Response: ${createPRResponse}"

                    def jsonResponse = new groovy.json.JsonSlurper().parseText(createPRResponse)
                    if (jsonResponse.message) {
                        error "Failed to create PR: ${jsonResponse.message}"
                    }
                }
            }
        }

        stage('Print Environment Variables') {
            steps {
                script {
                    echo "GITHUB_REPO: ${env.GITHUB_REPO}"
                    echo "GITHUB_USERNAME: ${env.GITHUB_USERNAME}"
                    echo "BRANCH_NAME: ${env.BRANCH_NAME}"
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
                    def prList = sh(script: """
                        curl -u ${env.GITHUB_USERNAME}:${env.GITHUB_CREDENTIALS_ID} -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${env.GITHUB_REPO}/pulls?head=${env.GITHUB_USERNAME}:${env.BRANCH_NAME}
                    """, returnStdout: true).trim()
                    echo "PR List: ${prList}"

                    def jsonSlurper = new groovy.json.JsonSlurper()
                    def prListParsed = jsonSlurper.parseText(prList)
                    echo "Parsed PR List: ${prListParsed}"

                    def prNumber = prListParsed.find { it.head.ref == "${env.BRANCH_NAME}" }?.number

                    if (prNumber == null) {
                        error "Failed to find PR number for branch: ${env.BRANCH_NAME}"
                    }

                    // Approve the pull request
                    def approvePR = """
                        curl -u ${env.GITHUB_USERNAME}:${env.GITHUB_CREDENTIALS_ID} -X POST -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${env.GITHUB_REPO}/pulls/${prNumber}/reviews -d '{
                            "body": "Approved by Jenkins",
                            "event": "APPROVE"
                        }'
                    """
                    sh approvePR
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
