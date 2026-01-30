environment {
  PATH = "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
}

pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare Environment') {
            steps {
                sh '''
                set -eux
                cp .env.example .env
                '''
            }
        }

        stage('Quality Gate: Lint + Format') {
            steps {
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
            archiveArtifacts artifacts: 'coverage_reports/html/**', allowEmptyArchive: true

            sh '''
            set +e
            docker compose down -v --remove-orphans
            '''
        }

        success {
            slackSend(
                channel: "#pipeline-updates"
                message: "Successfully built ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            )
        }

        failure {
            slackSend(
                channel: "#pipeline-updates"
                message: "Failed to build ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            )
        }
    }
}