pipeline {
  agent any

  stages {
    stage('CI (main + PR to main only)') {
      when {
        anyOf {
          branch 'main'
          changeRequest(target: 'main')
        }
      }

      stages {
        stage('Checkout') {
          steps {
            checkout scm
          }
        }

        stage('Build & Start Services') {
          steps {
            sh '''
              set -eux
              echo "PATH=$PATH"
              which docker || true
              docker compose down -v --remove-orphans || true
              docker compose up -d --build
              docker compose ps
            '''
          }
        }
      }
    }
  }

  post {
    always {
      sh '''
        set +e
        echo "=== Cleaning up containers/networks/volumes ==="
        docker compose down -v --remove-orphans
      '''
    }
  }
}