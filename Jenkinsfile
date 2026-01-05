pipeline {
    agent any

    environment {
        PATH_DOCKER = "/usr/local/bin"
        PYTHON_BIN  = "/Library/Developer/CommandLineTools/usr/bin/python3"

        DOCKER_IMAGE = "biprajit1999/mlops_assignment"
        DOCKER_TAG = "latest"
        CONTAINER_NAME = "mlops_assignment"
        APP_PORT = "5007"

        DOCKER_CREDENTIALS_ID = "DockerHub"
    }

    stages {

        stage("Checkout Code") {
            steps {
                git branch: 'master',
                    url: 'https://github.com/biprajit1999/mlops_assignment_grp123'
            }
        }

        stage("Install Dependencies") {
            steps {
                echo "Installing Python dependencies"
                sh """
                ${PYTHON_BIN} -m pip install --upgrade pip
                ${PYTHON_BIN} -m pip install -r requirements.txt
                """
            }
        }

        stage("Run Unit Tests (Pytest)") {
            steps {
                echo "Running unit tests"
                sh """
                ${PYTHON_BIN} -m pytest tests/ --disable-warnings
                """
            }
        }

        stage("Build Docker Image") {
            steps {
                withEnv(["PATH=$PATH:$PATH_DOCKER"]) {
                    sh """
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    """
                }
            }
        }

        stage("Push Image to Docker Hub") {
            steps {
                withEnv(["PATH=$PATH:$PATH_DOCKER"]) {
                    withCredentials([
                        usernamePassword(
                            credentialsId: DOCKER_CREDENTIALS_ID,
                            usernameVariable: 'DOCKER_USER',
                            passwordVariable: 'DOCKER_PASS'
                        )
                    ]) {
                        sh """
                        docker login -u ${DOCKER_USER} -p ${DOCKER_PASS}
                        docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                        """
                    }
                }
            }
        }

        stage("Deploy to Local Docker") {
            steps {
                withEnv(["PATH=$PATH:$PATH_DOCKER"]) {
                    sh """
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker pull ${DOCKER_IMAGE}:${DOCKER_TAG}
                    docker run -d \
                      --name ${CONTAINER_NAME} \
                      -p ${APP_PORT}:${APP_PORT} \
                      ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                }
            }
        }
    }

    post {
        success {
            echo "✅ CI/CD Pipeline completed successfully"
        }
        failure {
            echo "❌ CI/CD Pipeline failed"
        }
        always {
            withEnv(["PATH=$PATH:$PATH_DOCKER"]) {
                sh "docker image prune -f || true"
            }
        }
    }
}
