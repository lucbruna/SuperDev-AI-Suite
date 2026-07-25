# SuperDev AI Suite - Makefile
# Common development tasks

.PHONY: help install test lint format build run deploy clean

# Default target
help:
	@echo "SuperDev AI Suite - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install all dependencies"
	@echo "  make setup-dev     - Full development environment setup"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Start development servers (API + Frontend)"
	@echo "  make run-api       - Start only the API server"
	@echo "  make run-frontend  - Start only the frontend"
	@echo "  make run-worker    - Start background worker"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-integration - Run integration tests"
	@echo "  make test-e2e      - Run end-to-end tests"
	@echo "  make test-coverage - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run all linters"
	@echo "  make lint-python   - Lint Python code (ruff)"
	@echo "  make lint-typescript - Lint TypeScript (eslint)"
	@echo "  make lint-go       - Lint Go (golangci-lint)"
	@echo "  make lint-rust     - Lint Rust (clippy)"
	@echo "  make lint-docker   - Lint Dockerfiles (hadolint)"
	@echo "  make format        - Format all code"
	@echo "  make typecheck     - Run type checking"
	@echo ""
	@echo "Database:"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migrate-create - Create new migration"
	@echo "  make db-shell      - Open database shell"
	@echo "  make db-reset      - Reset database"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build all Docker images"
	@echo "  make docker-push   - Push Docker images"
	@echo "  make docker-scan   - Scan Docker images for vulnerabilities"
	@echo "  make docker-clean  - Clean Docker images/containers"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-staging   - Deploy to staging"
	@echo "  make deploy-prod      - Deploy to production"
	@echo "  make deploy-rollback  - Rollback deployment"
	@echo ""
	@ echo "Security:"
	@echo "  make security-scan   - Run security scans"
	@echo "  make sbom            - Generate SBOM"
	@echo "  make sign-images     - Sign Docker images"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean           - Clean build artifacts"
	@echo "  make clean-docker    - Clean Docker resources"
	@echo "  make clean-all       - Clean everything"

# Variables
PYTHON_VERSION := 3.12
NODE_VERSION := 20
GO_VERSION := 1.22
RUST_VERSION := 1.78

# Paths
BACKEND_DIR := backend
FRONTEND_DIR := admin-dashboard
SDK_GO_DIR := sdk/go
SDK_RUST_DIR := sdk/rust
SDK_PYTHON_DIR := sdk/python
SDK_TYPESCRIPT_DIR := sdk/typescript
INFRA_DIR := infrastructure

# Docker
REGISTRY := ghcr.io/superdev
IMAGE_TAG := latest

# Installation
install: install-python install-node install-go install-rust

install-python:
	@echo "Installing Python dependencies..."
	cd backend && poetry install --with dev,test

install-node:
	@echo "Installing Node.js dependencies..."
	cd admin-dashboard && npm ci

install-go:
	@echo "Installing Go dependencies..."
	cd sdk/go && go mod tidy && go mod download

install-rust:
	@echo "Installing Rust dependencies..."
	 cd sdk/rust && cargo fetch

# Development setup
setup-dev: install
	@echo "Setting up development environment..."
	cp .env.example .env
	@echo "Please edit .env with your configuration"
	@echo "Then run: make run"

# Development servers
run: run-api run-frontend

run-api:
	@echo "Starting API server..."
	cd backend && poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	@echo "Starting frontend..."
	cd admin-dashboard && npm run dev

run-worker:
	@echo "Starting worker..."
	cd backend && poetry run python -m worker.main

run-all: run-api run-frontend run-worker

# Testing
test: test-unit test-integration

test-unit:
	@echo "Running unit tests..."
	cd backend && poetry run pytest tests/unit -v --tb=short
	cd admin-dashboard && npm run test:unit

test-integration:
	@echo "Running integration tests..."
	cd backend && poetry run pytest tests/integration -v --tb=short

test-e2e:
	@echo "Running E2E tests..."
	cd admin-dashboard && npm run test:e2e

test-coverage:
	@echo "Running tests with coverage..."
	cd backend && poetry run pytest tests/ --cov=backend --cov-report=html --cov-report=term-missing
	cd admin-dashboard && npm run test:coverage

test-all: test-unit test-integration test-e2e

# Linting
lint: lint-python lint-typescript lint-go lint-rust lint-docker

lint-python:
	@echo "Linting Python code..."
	cd backend && poetry run ruff check . --output-format=github
	cd backend && poetry run ruff format --check .

lint-typescript:
	@echo "Linting TypeScript code..."
	cd admin-dashboard && npm run lint

lint-go:
	@echo "Linting Go code..."
	cd sdk/go && golangci-lint run ./...

lint-rust:
	@echo "Linting Rust code..."
	cd sdk/rust && cargo clippy --workspace --all-targets --all-features -- -D warnings

lint-docker:
	@echo "Linting Dockerfiles..."
	hadolint infrastructure/docker/Dockerfile.*

lint-terraform:
	@echo "Linting Terraform..."
	cd infrastructure/terraform && tflint

# Formatting
format: format-python format-typescript format-go format-rust

format-python:
	@echo "Formatting Python code..."
	cd backend && poetry run ruff format .
	cd backend && poetry run ruff check . --fix

format-typescript:
	@echo "Formatting TypeScript code..."
	cd admin-dashboard && npm run format

format-go:
	@echo "Formatting Go code..."
	cd sdk/go && go fmt ./...

format-rust:
	@echo "Formatting Rust code..."
	cd sdk/rust && cargo fmt --all

# Type checking
typecheck: typecheck-python typecheck-typescript

typecheck-python:
	@echo "Type checking Python..."
	cd backend && poetry run mypy --strict --ignore-missing-imports .

typecheck-typescript:
	@echo "Type checking TypeScript..."
	cd admin-dashboard && npx tsc --noEmit

# Database
migrate:
	@echo "Running database migrations..."
	cd backend && poetry run alembic upgrade head

migrate-create:
	@read -p "Migration message: " msg; \
	cd backend && poetry run alembic revision --autogenerate -m "$$msg"

migrate-downgrade:
	cd backend && poetry run alembic downgrade -1

migrate-reset:
	cd backend && poetry run alembic downgrade base && poetry run alembic upgrade head

db-shell:
	@echo "Opening database shell..."
	docker-compose -f infrastructure/docker/docker-compose.yml exec postgres psql -U superdev -d superdev

db-backup:
	@echo "Creating database backup..."
	docker-compose -f infrastructure/docker/docker-compose.yml exec postgres pg_dump -U superdev superdev > backup_$$(date +%Y%m%d_%H%M%S).sql

db-restore:
	@read -p "Backup file: " file; \
	docker-compose -f infrastructure/docker/docker-compose.yml exec -T postgres psql -U superdev superdev < $$file

# Docker
docker-build:
	@echo "Building Docker images..."
	docker build -t $(REGISTRY)/superdev-api:$(IMAGE_TAG) -f infrastructure/docker/Dockerfile.api .
	docker build -t $(REGISTRY)/superdev-frontend:$(IMAGE_TAG) -f infrastructure/docker/Dockerfile.frontend .
	docker build -t $(REGISTRY)/superdev-worker:$(IMAGE_TAG) -f infrastructure/docker/Dockerfile.worker .
	docker build -t $(REGISTRY)/superdev-sandbox:$(IMAGE_TAG) -f infrastructure/docker/Dockerfile.sandbox .

docker-push:
	@echo "Pushing Docker images..."
	docker push $(REGISTRY)/superdev-api:$(IMAGE_TAG)
	docker push $(REGISTRY)/superdev-frontend:$(IMAGE_TAG)
	docker push $(REGISTRY)/superdev-worker:$(IMAGE_TAG)
	docker push $(REGISTRY)/superdev-sandbox:$(IMAGE_TAG)

docker-scan:
	@echo "Scanning Docker images for vulnerabilities..."
	trivy image $(REGISTRY)/superdev-api:$(IMAGE_TAG)
	trivy image $(REGISTRY)/superdev-frontend:$(IMAGE_TAG)
	trivy image $(REGISTRY)/superdev-worker:$(IMAGE_TAG)
	trivy image $(REGISTRY)/superdev-sandbox:$(IMAGE_TAG)

docker-clean:
	@echo "Cleaning Docker resources..."
	docker system prune -af --volumes
	docker builder prune -af

# Deployment
deploy-staging:
	@echo "Deploying to staging..."
	kubectl apply -k infrastructure/kubernetes/overlays/staging
	argocd app sync superdev-staging

deploy-prod:
	@echo "Deploying to production..."
	kubectl apply -k infrastructure/kubernetes/overlays/production
	argocd app sync superdev-production

deploy-rollback:
	@read -p "Deployment name: " name; \
	argocd app rollback $$name

# Security
security-scan:
	@echo "Running security scans..."
	# SAST
	codeql database create /tmp/codeql-db --language=python,javascript,go,rust
	codeql database analyze /tmp/codeql-db --format=sarif-latest --output=/tmp/results.sarif
	# Dependency scanning
	trivy fs --security-checks vuln,secret,config .
	# Container scanning
	trivy image $(REGISTRY)/superdev-api:$(IMAGE_TAG)
	trivy image $(REGISTRY)/superdev-frontend:$(IMAGE_TAG)

sbom:
	@echo "Generating SBOM..."
	syft packages dir:. -o spdx-json=sbom.spdx.json
	syft packages dir:. -o cyclonedx-json=sbom.cyclonedx.json

sign-images:
	@echo "Signing Docker images..."
	cosign sign --yes $(REGISTRY)/superdev-api:$(IMAGE_TAG)
	cosign sign --yes $(REGISTRY)/superdev-frontend:$(IMAGE_TAG)
	cosign sign --yes $(REGISTRY)/superdev-worker:$(IMAGE_TAG)
	cosign sign --yes $(REGISTRY)/superdev-sandbox:$(IMAGE_TAG)

# Cleanup
clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "target" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.egg" -exec rm -rf {} + 2>/dev/null || true

clean-docker:
	@echo "Cleaning Docker resources..."
	docker system prune -af --volumes
	docker builder prune -af

clean-all: clean clean-docker

# CI/CD
ci: lint test security-scan

cd: ci deploy-staging

# Development utilities
dev-logs:
	docker-compose -f infrastructure/docker/docker-compose.yml logs -f

dev-shell:
	docker-compose -f infrastructure/docker/docker-compose.yml exec backend bash

dev-psql:
	docker-compose -f infrastructure/docker/docker-compose.yml exec postgres psql -U superdev -d superdev

dev-redis:
	docker-compose -f infrastructure/docker/docker-compose.yml exec redis redis-cli

# Documentation
docs:
	@echo "Generating documentation..."
	cd backend && poetry run sphinx-build -b html docs docs/_build/html
	cd admin-dashboard && npm run docs

docs-serve:
	cd backend/docs/_build/html && python -m http.server 8080

# Release
release:
	@read -p "Version: " version; \
	git tag -a v$$version -m "Release v$$version"; \
	git push origin v$$version

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "API: DOWN"
	@curl -f http://localhost:3000/health || echo "Frontend: DOWN"

# Watch mode
watch:
	@echo "Starting file watcher..."
	@while true; do \
		inotifywait -r -e modify,create,delete backend/ admin-dashboard/src/ sdk/; \
		make test; \
	done

# Profile
profile:
	@echo "Running profiling..."
	cd backend && poetry run python -m cProfile -o profile.stats -m pytest tests/ -v
	cd backend && poetry run snakeviz profile.stats

# Benchmark
benchmark:
	@echo "Running benchmarks..."
	cd backend && poetry run pytest tests/benchmark -v --benchmark-only