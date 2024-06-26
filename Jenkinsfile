pipeline {
    agent {
        kubernetes {
            label 'jenkins-agent-pod'
            idleMinutes 1
            yamlFile './helm/jenkins/build-pod.yaml'
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
        JIRA_ISSUE_KEY = ''
    }

    stages {
        stage('Setup') {
            steps {
                checkout scm
                script {
                    def initEnv = { echo 'Environment setup initialized' }
                    def getUniqueBuildIdentifier = { suffix = '' ->
                        def now = new Date()
                        def formattedDate = now.format("yyyyMMdd-HHmmss", TimeZone.getTimeZone('UTC'))
                        return formattedDate + (suffix ? '-' + suffix : '')
                    }
                    initEnv()
                    def id = getUniqueBuildIdentifier()
                    if (env.BRANCH_NAME == 'main') {
                        env.BUILD_ID = "1." + id
                    } else {
                        env.BUILD_ID = "0." + id
                    }
                    currentBuild.displayName += " {build-name:" + env.BUILD_ID + "}"
                    
                    // Extract Jira issue key from branch name
                    def branchName = env.BRANCH_NAME
                    def match = branchName =~ /([A-Z]+-\d+)/
                    if (match) {
                        env.JIRA_ISSUE_KEY = match[0][1]
                    }
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

        stage('Create Pull Request (feature)') {
            when {
                branch 'feature'
            }
            steps {
                script {
                    withCredentials([string(credentialsId: 'git-secret', variable: 'GIT_TOKEN')]) {
                        def createPR = """
                            curl -u ${env.GITHUB_USERNAME}:${env.GIT_TOKEN} -X POST -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${env.GITHUB_REPO}/pulls -d '{
                                "title": "Auto PR from Jenkins: ${env.BUILD_ID}",
                                "head": "${env.BRANCH_NAME}",
                                "base": "main",
                                "body": "This PR addresses ${env.JIRA_ISSUE_KEY}"
                            }'
                        """
                        sh createPR
                    }
                }
            }
        }

        stage('Manual Approval (feature)') {
            when {
                branch 'feature'
            }
            steps {
                script {
                    input message: 'Approve the merge to main?', ok: 'Approve'
                }
            }
        }

        stage('Merge Feature Branch (feature)') {
            when {
                branch 'feature'
            }
            steps {
                script {
                    withCredentials([string(credentialsId: 'git-secret', variable: 'GIT_TOKEN')]) {
                        def prList = sh(script: """
                            curl -u ${env.GITHUB_USERNAME}:${env.GIT_TOKEN} -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${env.GITHUB_REPO}/pulls?head=${env.GITHUB_USERNAME}:${env.BRANCH_NAME}
                        """, returnStdout: true).trim()
                        def prNumber = new groovy.json.JsonSlurper().parseText(prList).find { it.head.ref == "${env.BRANCH_NAME}" }.number
                        def mergePR = """
                            curl -u ${env.GITHUB_USERNAME}:${env.GIT_TOKEN} -X PUT -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${env.GITHUB_REPO}/pulls/${prNumber}/merge
                        """
                        sh(mergePR)
                    }
                }
            }
        }

        stage('Push Docker Image (main)') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry('https://registry.hub.docker.com', env.DOCKER_CREDENTIALS_ID) {
                        dockerImage.push("${env.BUILD_ID}")
                        dockerImage.push('latest')
                    }
                }
            }
        }
    }
}
