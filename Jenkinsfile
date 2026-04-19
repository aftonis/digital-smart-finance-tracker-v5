pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                sh 'pytest tests/ -v'
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t smart-finance-tracker .'
            }
        }

        stage('Push to GitHub') {
            steps {
                sh 'git push origin master'
            }
        }
    }

    post {
        success {
            echo 'Pipeline complete — Streamlit Cloud will redeploy automatically.'
        }
        failure {
            echo 'Pipeline failed — check the logs above.'
        }
    }
}
