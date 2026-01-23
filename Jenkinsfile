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