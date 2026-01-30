pipeline {
    agent none

    environment {
        PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    }

    stages {
        stage('Checkout') {
            agent any
            steps {
                checkout scm
            }
        }

        stage('Prepare Environment') {
            agent any
            steps {
                sh '''
                set -eux
                cp .env.example .env
                stash name: 'workspace',
                    includes: '**/*',
                    excludes: '.git/**, db_data/**, coverage_reports/**, **/__pycache__/**, **/*.pyc, .venv/**'
                '''
            }
        }

        stage('Quality Gate: Lint + Format') {
            agent { label 'docker' }
            steps {
                unstash 'workspace'
                script {
                    def status = sh(
                        script: '''
                        set -eu
                        docker compose run --rm lint
                        ''',
                        returnStatus: true
                    )

                    if (status != 0) {
                        error("""Quality Gate FAILED: Lint / Format checks did not pass.
                        To fix, run {ruff check .} and {black .} locally and rerun the checks
                        using {ruff check .} and {black --check .}. Commit the changes and push again.""")
                    }
                }
            }
        }

        stage('Build & Start Services') {
            agent { label 'docker' }
            steps {
                sh '''
                    set -eux
                    docker compose down -v --remove-orphans || true
                    docker compose up -d --build
                    docker compose ps
                '''
            }
        }

        stage('Tests + Coverage (HTML)') {
            agent { label 'docker' }
            steps {
                sh '''
                set -eux
                docker compose run --rm test
                '''
            }
        }
    }

    post {
        always {
            node('docker') {
                archiveArtifacts artifacts: 'coverage_reports/html/**', allowEmptyArchive: true

                sh '''
                set +e
                docker compose down -v --remove-orphans
                '''
            }
        }

        success {
            slackSend(
                channel: "#pipeline-updates",
                message: "Successfully built ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            )
        }

        failure {
            node('built-in') {
                script {
                    withCredentials([usernamePassword(credentialsId: 'jenkins-api', usernameVariable: 'J_USER', passwordVariable: 'J_TOKEN')]) {
                        def logTail = sh(
                            script: '''
                            set -eu
                            curl -s -u "$J_USER:$J_TOKEN" "${BUILD_URL}consoleText" | tail -n 80''')
                        def msg = """Failed to build ${env.JOB_NAME} #${env.BUILD_NUMBER}
                        console output last 80 lines:
                        ```$logTail```"""
                        slackSend(
                            channel: "#pipeline-updates",
                            message: msg
                        )
                    }
                }
            }
        }
    }
}