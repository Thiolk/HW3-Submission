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
                cp .env.example .env'''
                
                stash name: 'workspace',
                    includes: '**/*',
                    excludes: '.git/**, db_data/**, coverage_reports/**, **/__pycache__/**, **/*.pyc, .venv/**'
                
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
                unstash 'workspace'
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
                unstash 'workspace'
                sh '''
                set -eux
                docker compose run --rm test
                '''
            }
        }

        stage('SonarQube Scan') {
            agent { label 'docker' }
            steps {
                unstash 'workspace'
                withSonarQubeEnv('sonarqube-local') {
                    sh '''
                    set -eu
                    mkdir -p .scannerwork
                    docker run --rm \
                        -e SONAR_HOST_URL="http://host.docker.internal:9000" \
                        -e SONAR_TOKEN="$SONAR_AUTH_TOKEN" \
                        -v "$WORKSPACE:/usr/src" \
                        -w /usr/src \
                        sonarsource/sonar-scanner-cli:latest \
                        -Dsonar.userHome=/usr/src \
                        -Dsonar.working.directory=.scannerwork
                    '''
                }
            }
        }

        stage('Quality Gate') {
            agent { label 'docker' }
            steps {
                unstash 'workspace'
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build and Package Artifact') {
            agent { label 'docker' }
            steps {
                unstash 'workspace'
                script {
                    def VERSION = "0.1.${env.BUILD_NUMBER}"
                    def IMAGE = "todo-app:${VERSION}"

                    sh """
                    set -eux
                    mkdir -p artifacts
                    docker build -t ${IMAGE} ./app
                    docker save ${IMAGE} | gzip > artifacts/todo-app_${VERSION}.tar.gz
                    """
                }
            }
        }

        stage('Prepare Staging Env') {
            agent any
            steps {
                sh 'cp .env.staging.example .env.staging'
                stash name: 'staging', includes: '**/*', excludes: '.git/**, **/__pycache__/**, **/*.pyc, .venv/**'
            }
        }

        stage('Staging DB Up (seeded)') {
            when { branch 'main' }
            agent { label 'docker' }
            steps {
                unstash 'staging'
                sh '''
                    set -eux
                    docker compose --env-file .env.staging --profile staging down -v || true
                    docker compose --env-file .env.staging --profile staging up -d staging-db
                    docker compose --env-file .env.staging --profile staging ps
                    sleep 15
                    docker compose --env-file .env.staging --profile staging exec -T staging-db sh -lc '
                    echo "MYSQL_DATABASE=$MYSQL_DATABASE"
                    mysql -h 127.0.0.1 -P 3306 -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "
                    SHOW TABLES;
                    SELECT COUNT(*) AS task_count FROM task;
                    SELECT * FROM task;"'
                    docker compose --env-file .env.staging --profile staging down -v 
                '''
            }
        }

        stage('E2E Tests (Playwright)') {
        agent { label 'docker' }
        steps {
            unstash 'staging'
            sh '''
                set -eux
                docker compose --env-file .env.staging --profile staging up -d --build staging-db staging-web
                docker compose --env-file .env.staging --profile staging run --rm e2e
            ls -la e2e/test-results || true
            '''
            stash name: 'e2e-junit', includes: 'e2e/test-results/**', allowEmpty: true
            }
        }
    }

    post {
        always {
            node('docker') {
                archiveArtifacts artifacts: 'coverage_reports/html/**', allowEmptyArchive: true
                archiveArtifacts artifacts: 'artifacts/**', allowEmptyArchive: true
                unstash 'e2e-junit'
                junit testResults: 'e2e/test-results/results.xml', allowEmptyResults: true
                archiveArtifacts artifacts: 'e2e/test-results/**', allowEmptyArchive: true

                sh '''
                set +e
                docker compose --env-file .env.staging --profile staging down -v --remove-orphans || true
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
            slackSend(
                channel: "#pipeline-updates",
                message: "failed to build ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            )
        }
    }
}