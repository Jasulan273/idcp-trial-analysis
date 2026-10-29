pipeline {
    agent any
    options {
        timestamps()
        disableConcurrentBuilds()
        skipDefaultCheckout(true)
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }
    triggers { pollSCM('* * * * *') }
    environment {
        IMAGE = "idcp-trial-analysis:build-${BUILD_NUMBER}"
        TEST_IMAGE = "idcp-trial-analysis:test-${BUILD_NUMBER}"
        RUN_NAME = "idcp-analysis-${BUILD_NUMBER}"
    }
    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                checkout scm
                sh 'git rev-parse HEAD'
            }
        }
        stage('Unit tests') {
            steps {
                sh '''
                    docker build --target test -t "$TEST_IMAGE" .
                    docker run --rm --network none "$TEST_IMAGE"
                '''
            }
        }
        stage('Build image') {
            steps {
                sh 'docker build --target runtime -t "$IMAGE" .'
            }
        }
        stage('Run analysis') {
            steps {
                sh '''
                    mkdir -p build-results
                    docker run --name "$RUN_NAME" --network none "$IMAGE"
                    docker cp "$RUN_NAME":/work/results/. build-results/
                    {
                        printf 'commit='; git rev-parse HEAD
                        printf 'image_id='; docker image inspect --format '{{.Id}}' "$IMAGE"
                        printf 'container_user='; docker image inspect --format '{{.Config.User}}' "$IMAGE"
                        docker version --format 'engine={{.Server.Version}}'
                        sha256sum data/example_pairs.csv build-results/summary.json
                    } > build-results/provenance.txt
                    docker rm "$RUN_NAME"
                '''
            }
        }
        stage('Archive results') {
            steps {
                archiveArtifacts artifacts: 'build-results/*', fingerprint: true
            }
        }
    }
    post {
        always {
            sh 'docker rm -f "$RUN_NAME" >/dev/null 2>&1 || true'
            sh 'docker image rm "$TEST_IMAGE" >/dev/null 2>&1 || true'
        }
    }
}
