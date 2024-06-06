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
        GITHUB_CREDENTIALS_ID = 'git-token'
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
                    // Create a pull request from the feature branch to the main branch using GitHub API
                    def createPR = """
                        curl -u ${env.GITHUB_USERNAME}:${env.GITHUB_CREDENTIALS_ID} -X POST -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${env.GITHUB_REPO}/pulls -d '{
                            "title": "Auto PR from Jenkins: ${env.BUILD_ID}",
                            "head": "${env.BRANCH_NAME}",
                            "base": "main"
                        }'
                    """
                    sh createPR
                }
            }
        }

        stage('Manual Approval') {
            when {
                branch 'feature'
            }
            steps {
                input message: 'Approve the merge to main?', ok: 'Approve'
            }
        }

        stage('Merge Pull Request') {
            when {
                branch 'feature'
            }
            steps {
                script {
                    // Merge the pull request using GitHub API
                    def mergePR = """
                        PR_NUMBER=$(curl -u ${env.GITHUB_USERNAME}:${env.GITHUB_CREDENTIALS_ID} -s https://api.github.com/repos/${env.GITHUB_REPO}/pulls?head=${env.GITHUB_USERNAME}:${env.BRANCH_NAME} | jq -r '.[0].number')
                        curl -u ${env.GITHUB_USERNAME}:${env.GITHUB_CREDENTIALS_ID} -X PUT -H "Accept: application/vnd.github.v3+json" https://api.github.com/repos/${env.GITHUB_REPO}/pulls/${PR_NUMBER}/merge -d '{
                            "commit_title": "Merge pull request #${PR_NUMBER} from ${env.BRANCH_NAME} to main",
                            "merge_method": "merge"
                        }'
                    """
                    sh mergePR
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
