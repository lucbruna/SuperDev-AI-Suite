# Makefile for {{project_name}}

.PHONY: help install dev test lint format type-check migrate migrate-create run docker-build docker-up docker-down clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install        - Install dependencies"
	@echo "  dev            - Install dev dependencies"
	@echo "  test           - Run tests"
	@echo "  test-cov       - Run tests with coverage"
	@echo "  lint           - Run linter"
	@echo "  format         - Format code"
	@echo "  type-check     - Run type checker"
	@echo "  migrate        - Run database migrations"
	@echo "  migrate-create - Create new migration"
	@echo "  run            - Run development server"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-up      - Start Docker services"
	@echo "  docker-down    - Stop Docker services"
	@echo "  docker-logs    - View Docker logs"
	@echo "  clean          - Clean build artifacts"

# Python and pip
PYTHON := python
PIP := pip
UVICORN := uvicorn
ALEMBIC := alembic
PYTEST := pytest
RUFF := ruff
MYPY := mypy
PRE_COMMIT := pre-commit

# Install dependencies
install:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e .

# Install with dev dependencies
dev:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e ".[dev]"
	$(PRE_COMMIT) install

# Run tests
test:
	$(PYTEST) -v

# Run tests with coverage
test-cov:
	$(PYTEST) -v --cov={{project_name}} --cov-report=term-missing --cov-report=html --cov-report=xml

# Run linter
lint:
	$(RUFF) check src tests

# Format code
format:
	$(RUFF) format src tests

# Type check
type-check:
	$(MYPY) src

# Run all checks
check: lint type-check test

# Database migrations
migrate:
	$(ALEMBIC) upgrade head

migrate-create:
	@read -p "Migration message: " msg; \
	$(ALEMBIC) revision --autogenerate -m "$$msg"

# Run development server
run:
	$(UVICORN) {{project_name}}.main:app --reload --host 0.0.0.0 --port 8000

# Run production server
run-prod:
	$(UVICORN) {{project_name}}.main:app --host 0.0.0.0 --port 8000 --workers 4

# Docker commands
docker-build:
	docker build -t {{project_name}} -f docker/Dockerfile ..

docker-up:
	docker-compose -f docker/docker-compose.yml up -d

docker-down:
	docker-compose -f docker/docker-compose.yml down

docker-logs:
	docker-compose -f docker/docker-compose.yml logs -f

docker-ps:
	docker-compose -f docker/docker-compose.yml ps

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov .coverage dist build *.egg-info 2>/dev/null || true

# Pre-commit
pre-commit:
	$(PRE_COMMIT) run --all-files

# Generate requirements.txt
requirements:
	$(PIP) freeze > requirements.txt

# Database shell
dbshell:
	$(ALEMBIC) -x db_url=postgresql+asyncpg://postgres:postgres@localhost:5432/{{project_name}} downgrade base
	$(ALEMBIC) -x db_url=postgresql+asyncpg://postgres:postgres@localhost:5432/{{project_name}} upgrade head

# Seed database
seed:
	$(PYTHON) -m scripts.seed_db