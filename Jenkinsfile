pipeline {
    agent any

    stages {
        stage('Backend tests') {
            steps {
                sh './scripts/test.sh backend'
            }
        }

        stage('Frontend tests') {
            steps {
                sh './scripts/test.sh frontend'
            }
        }
    }

    post {
        always {
            sh 'docker compose down -v --remove-orphans || true'
        }
    }
}
