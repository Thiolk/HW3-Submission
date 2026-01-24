# HW3-Submission

Prequisites
Git
Docker Desktop
Jenkins (running locally)
ngrok

Project Overview
This project runs a Flask TODO app with a MySQL backend using Docker Compose, and includes a Jenkins CI pipeline with:
Linting + formatting quality gate using Ruff + Black
Code Testing via PyTest
Coverage report generation (HTML) with minimum coverage threshold of 80%
Automatic cleanup after each pipeline run

Services in docker-compose.yml:
web — Flask app
db — MySQL database
nginx — nginx reverse proxy
lint — Ruff + Black
test — Pytest + Coverage

This project uses a .env file for environment variables.
Copy from the template using the command `cp .env.example .env`

Start up the containers
`docker compose up -d --build`

Access the app through the reverse proxy
`http://localhost/`

Stop the containers
`docker compose down`

To check for code quality, run
`docker compose run --rm lint`

To fix any issues
`ruff check .`
`black .`

To run the PyTests
`docker compose run --rm test`

Code coverage report can be found at: coverage_reports/html/index.html

CI Pipeline (Jenkins)

The pipeline automatically runs:
1. Checkout source code
2. Create .env from .env.example
3. Quality Gate: Ruff + Black
4. Build and start services
5. Run tests + coverage (HTML)
6. Archive coverage report artifacts
7. Cleanup containers and volumes

The pipeline fails automatically if:
1. lint/format fails
2. tests fail
3. coverage drops below 80%

Setup Github Webhook
Run Jenkins locally at http://localhost:8080
ngrok http 8080
https://xxxxxx.ngrok-dev.app
In the github repo, 
1. set the payload url to https://xxxxxx.ngrok-dev.app/github-webhook/
2. Content type: application/json
3. Events: enable push events and pull request events