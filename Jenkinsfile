// ==============================================================================
// Jenkinsfile — General Development System (GDS) (CI/CD Pipeline)
// ==============================================================================

pipeline {
    agent any

    environment {
        PROJECT_DIR   = '/opt/GDSV2'
        COMPOSE_DIR   = "${PROJECT_DIR}/deployment/docker"
        IMAGE_NAME    = 'gds-django'
        IMAGE_TAG     = "build-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                dir("${PROJECT_DIR}") {
                    git branch: 'main',
                        url: 'https://github.com/abdalazeim/GDS.git'
                }
            }
        }

        stage('Stop Old Containers') {
            steps {
                dir("${COMPOSE_DIR}") {
                    sh 'docker compose down --remove-orphans || true'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir("${COMPOSE_DIR}") {
                    sh "docker compose build --no-cache"
                    sh "docker tag gds-django:latest ${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker tag gds-django:latest ${IMAGE_NAME}:latest"
                }
            }
        }

        stage('Start Services') {
            steps {
                dir("${COMPOSE_DIR}") {
                    sh 'docker compose up -d'
                }
            }
        }

        stage('Wait for Healthy') {
            steps {
                sh '''
                    echo "Waiting for services to become healthy..."
                    for i in $(seq 1 60); do
                        STATUS=$(docker inspect --format='{{.State.Health.Status}}' docker-django-1 2>/dev/null || echo "starting")
                        echo "  [$i/60] Django status: $STATUS"
                        if [ "$STATUS" = "healthy" ]; then
                            echo "  Application is healthy!"
                            exit 0
                        fi
                        sleep 5
                    done
                    echo "Application did not become healthy in time"
                    docker compose logs django
                    exit 1
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/)
                    echo "HTTP Status: $HTTP_CODE"
                    if [ "$HTTP_CODE" = "200" ]; then
                        echo "Smoke test passed"
                    else
                        echo "Smoke test failed (HTTP $HTTP_CODE)"
                        exit 1
                    fi
                '''
            }
        }

        stage('Verify Logs') {
            steps {
                dir("${COMPOSE_DIR}") {
                    sh 'docker compose logs --tail=20 django'
                }
            }
        }
    }

    post {
        success {
            echo """
            Pipeline completed successfully!
            ===========================
            Image: ${IMAGE_NAME}:${IMAGE_TAG}
            App:   http://localhost:8001
            DB:    localhost:5433
            Redis: localhost:6380
            ===========================
            """
        }
        failure {
            dir("${COMPOSE_DIR}") {
                sh 'docker compose logs --tail=50 django || true'
            }
            echo "Pipeline failed! Check logs above."
        }
        always {
            dir("${COMPOSE_DIR}") {
                sh 'docker compose ps || true'
            }
        }
    }
}
