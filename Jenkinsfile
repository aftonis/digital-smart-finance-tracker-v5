/*
 * Digital Smart Finance Tracker v5 — CI/CD Pipeline
 * Quartet Protocol — Mission Charlie: Analyst + Reporting Engine
 *
 * Mirrors the Agentic Development Life Cycle (ADLC):
 *   Stage 1 — PLAN    : checkout, validate structure, check secrets hygiene
 *   Stage 2 — DESIGN  : install deps, lint, unit tests
 *   Stage 3 — EXECUTE : build Docker image, smoke-test container
 *   Stage 4 — DEPLOY  : tag image as latest, report deployment status
 */

pipeline {
    agent any

    environment {
        IMAGE_NAME  = "digital-smart-finance-tracker-v5"
        IMAGE_TAG   = "${env.BUILD_NUMBER}"
        APP_PORT    = "8501"
        TEST_CONTAINER = "finance-tracker-test-${env.BUILD_NUMBER}"
    }

    options {
        timeout(time: 20, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    stages {

        // ── ADLC PHASE 1: PLAN ────────────────────────────────────────────
        stage('Plan — Validate') {
            steps {
                echo '╔══════════════════════════════════╗'
                echo '║  ADLC Phase 1: PLAN              ║'
                echo '╚══════════════════════════════════╝'

                checkout scm

                echo 'Validating project structure...'
                sh '''
                    echo "--- Required files ---"
                    test -f requirements.txt  && echo "✔ requirements.txt" || (echo "✘ requirements.txt MISSING" && exit 1)
                    test -f Dockerfile        && echo "✔ Dockerfile"       || (echo "✘ Dockerfile MISSING"       && exit 1)
                    test -f app/streamlit_app.py && echo "✔ streamlit_app.py" || (echo "✘ streamlit_app.py MISSING" && exit 1)
                    test -f src/crew.py       && echo "✔ src/crew.py"      || (echo "✘ src/crew.py MISSING"      && exit 1)
                    test -f src/tools/calculators.py && echo "✔ calculators.py" || (echo "✘ calculators.py MISSING" && exit 1)
                    test -d tests             && echo "✔ tests/ directory" || (echo "✘ tests/ MISSING"           && exit 1)

                    echo ""
                    echo "--- Secrets hygiene check ---"
                    LEAKED=$(grep -r "sk-ant-api03-" . --include="*.py" --include="*.yml" --include="*.yaml" 2>/dev/null | grep -v "example" | grep -v "\.\.\." | grep -v "your_" | grep -v "REPLACE_WITH" || true)
                    if [ -n "$LEAKED" ]; then
                        echo "✘ HARD-CODED ANTHROPIC KEY DETECTED — build aborted"
                        exit 1
                    fi
                    LEAKED2=$(grep -r "sk-proj-" . --include="*.py" --include="*.yml" 2>/dev/null | grep -v "example" | grep -v "\.\.\." | grep -v "your_" || true)
                    if [ -n "$LEAKED2" ]; then
                        echo "✘ HARD-CODED OPENAI KEY DETECTED — build aborted"
                        exit 1
                    fi
                    echo "✔ No hard-coded secrets found"

                    echo ""
                    echo "--- .gitignore check ---"
                    grep -q "^.env$" .gitignore && echo "✔ .env is gitignored" || (echo "✘ .env not in .gitignore!" && exit 1)
                    grep -q "secrets.toml" .gitignore && echo "✔ secrets.toml is gitignored" || (echo "✘ secrets.toml not in .gitignore!" && exit 1)
                '''
            }
        }

        // ── ADLC PHASE 2: DESIGN ─────────────────────────────────────────
        stage('Design — Test') {
            steps {
                echo '╔══════════════════════════════════╗'
                echo '║  ADLC Phase 2: DESIGN            ║'
                echo '╚══════════════════════════════════╝'

                echo 'Running unit tests inside isolated Docker container...'
                sh '''
                    docker run --rm \
                        --name finance-tracker-ci-${BUILD_NUMBER} \
                        -v "$(pwd)":/app \
                        -w /app \
                        python:3.12-slim \
                        bash -c "
                            pip install --quiet --no-cache-dir \
                                pytest pandas plotly streamlit python-dotenv pydantic \
                                crewai>=0.80.0 crewai-tools>=0.15.0 \
                                requests pyyaml numpy 2>&1 | tail -5 &&
                            echo '--- Running test suite ---' &&
                            pytest tests/ -v --tb=short 2>&1
                        "
                '''
            }
            post {
                always {
                    sh "docker rm -f finance-tracker-ci-${BUILD_NUMBER} 2>/dev/null || true"
                }
            }
        }

        // ── ADLC PHASE 3: EXECUTE ─────────────────────────────────────────
        stage('Execute — Docker Build') {
            steps {
                echo '╔══════════════════════════════════╗'
                echo '║  ADLC Phase 3: EXECUTE           ║'
                echo '╚══════════════════════════════════╝'

                echo "Building Docker image: ${IMAGE_NAME}:${IMAGE_TAG}"
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."

                echo 'Running container smoke test (HTTP 200 on port 8501)...'
                sh '''
                    docker run -d \
                        --name $TEST_CONTAINER \
                        -p 8502:8501 \
                        -e ANTHROPIC_API_KEY=smoke-test-key \
                        -e CLAUDE_MODEL=claude-3-5-haiku-20241022 \
                        $IMAGE_NAME:$IMAGE_TAG

                    echo "Waiting for app to boot..."
                    sleep 15

                    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8502 || echo "000")
                    echo "HTTP Status: $STATUS"

                    docker stop $TEST_CONTAINER && docker rm $TEST_CONTAINER

                    if [ "$STATUS" = "200" ]; then
                        echo "✔ Smoke test passed — app serves HTTP 200"
                    else
                        echo "✘ Smoke test FAILED — got HTTP $STATUS"
                        exit 1
                    fi
                '''
            }
            post {
                always {
                    sh "docker rm -f ${TEST_CONTAINER} 2>/dev/null || true"
                }
            }
        }

        // ── ADLC PHASE 4: DEPLOY ──────────────────────────────────────────
        stage('Deploy — Tag & Report') {
            steps {
                echo '╔══════════════════════════════════╗'
                echo '║  ADLC Phase 4: DEPLOY            ║'
                echo '╚══════════════════════════════════╝'

                sh '''
                    echo "Tagging image as latest..."
                    docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest

                    echo ""
                    echo "╔══════════════════════════════════════════════════╗"
                    echo "║  BUILD #$BUILD_NUMBER COMPLETE                    "
                    echo "║  Image : $IMAGE_NAME:$IMAGE_TAG                   "
                    echo "║  Tagged: $IMAGE_NAME:latest                       "
                    echo "║  Deploy: docker compose up -d app                 "
                    echo "║  Cloud : push to GitHub → Streamlit auto-redeploy "
                    echo "╚══════════════════════════════════════════════════╝"
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline PASSED — Build #${env.BUILD_NUMBER} ready to ship."
        }
        failure {
            echo "❌ Pipeline FAILED — review logs above. Fix → re-push → Jenkins re-runs automatically."
        }
        always {
            // Clean up any leftover test containers
            sh "docker rm -f finance-tracker-ci-${BUILD_NUMBER} ${TEST_CONTAINER} 2>/dev/null || true"
            deleteDir()   // built-in — no plugin required
        }
    }
}
