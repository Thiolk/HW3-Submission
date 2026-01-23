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
                export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
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

    stage('Tests + Coverage (HTML)') {
        steps {
            sh '''
            set -eux
            export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
            docker compose run --rm test
            '''
        }
    }

    stage('Build & Start Services') {
      steps {
        sh '''
          set -eux
          export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
          docker compose down -v --remove-orphans || true
          docker compose up -d --build
          docker compose ps
        '''
      }
    }

    stage('Run Tests') {
        steps {
            sh '''
            set -eux
            export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

            # Run pytest inside the web container (no TTY in Jenkins)
            docker compose exec -T web pytest -q
            '''
        }
    }
    
  }

  post {
    always {
      archiveArtifacts artifacts: 'coverage_reports/html/**', allowEmptyArchive: true

      sh '''
        set +e
        export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
        docker compose down -v --remove-orphans
      '''
    }
  }
}