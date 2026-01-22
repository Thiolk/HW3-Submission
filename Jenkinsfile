pipeline {
  agent any

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

  post {
    always {
      sh '''
        set +e
        docker compose down -v --remove-orphans
      '''
    }
  }
}