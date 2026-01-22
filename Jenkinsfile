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

          # Clean up any leftovers from previous runs (safe)
          docker compose down -v --remove-orphans || true

          # Build images + start containers
          docker compose up -d --build

          # Show what's running
          docker compose ps
        '''
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