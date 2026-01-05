pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "docker.io/biprajit1999/mlops_assignment"
        DOCKER_TAG = "latest"
        CONTAINER_NAME = "mlops_assignment"
        APP_PORT = "5007"
        DOCKER_CREDENTIALS_ID = "DockerHub"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/biprajit1999/mlops_assignment_grp123'
            }
        }
        

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                }
            }
        }

        stage('Push Image to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS_ID) {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                    }
                }
            }
        }

        stage('Deploy to Local Docker (CD)') {
            steps {
                script {
                    sh """
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true

                    docker pull ${DOCKER_IMAGE}:${DOCKER_TAG}

                    docker run -d \\
                      --name ${CONTAINER_NAME} \\
                      -p ${APP_PORT}:${APP_PORT} \\
                      ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "Deployment successful 🚀"
        }
        failure {
            echo "Pipeline failed ❌"
        }
    }
}
