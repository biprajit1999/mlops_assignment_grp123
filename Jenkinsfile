pipeline {
    agent any

    environment {
        // Docker binary path (macOS)
        PATH_DOCKER = "/usr/local/bin"

        // App / Image details
        DOCKER_IMAGE = "biprajit1999/mlops_assignment"
        DOCKER_TAG = "latest"
        CONTAINER_NAME = "mlops_assignment"
        APP_PORT = "5007"

        // Jenkins credentials ID for Docker Hub
        DOCKER_CREDENTIALS_ID = "DockerHub"
    }

    stages {

        stage("Checkout Code") {
            steps {
                echo "Cloning GitHub repository"
                git branch: 'master',
                    url: 'https://github.com/biprajit1999/mlops_assignment_grp123'
            }
        }

        /* ===================== NEW STAGE ===================== */
        stage("Setup Python Environment") {
            steps {
                echo "Setting up Python environment"
                sh """
                python3 --version
                python3 -m pip install --upgrade pip
                pip install -r requirements.txt
                pip install pytest flake8
                """
            }
        }

        /* ===================== NEW STAGE ===================== */
        stage("Linting (Code Quality Check)") {
            steps {
                echo "Running flake8 linting"
                sh """
                flake8 . --exclude=venv,__pycache__ --max-line-length=100 || true
                """
            }
        }

        /* ===================== NEW STAGE ===================== */
        stage("Unit Tests (Pytest)") {
            steps {
                echo "Running unit tests"
                sh """
                pytest tests/ --junitxml=reports/unit_test_report.xml
                """
            }
        }

        /* ===================== NEW STAGE ===================== */
        stage("Build Docker Image") {
            steps {
                echo "Building Docker image"
                withEnv(["PATH=$PATH:$PATH_DOCKER"]) {
                    sh """
                    docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                    """
                }
            }
        }

        stage("Push Image to Docker Hub") {
            steps {
                echo "Pushing image to Docker Hub"
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

        stage("Deploy to Local Docker (CD)") {
            steps {
                echo "Deploying container locally"
                withEnv(["PATH=$PATH:$PATH_DOCKER"]) {
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
            echo "✅ CI/CD Pipeline completed successfully 🚀"
        }
        failure {
            echo "❌ CI/CD Pipeline failed"
        }
        always {
            echo "Archiving test reports"
            archiveArtifacts artifacts: 'reports/*.xml', allowEmptyArchive: true

            echo "Cleaning up unused Docker images"
            withEnv(["PATH=$PATH:$PATH_DOCKER"]) {
                sh "docker image prune -f || true"
            }
        }
    }
}
