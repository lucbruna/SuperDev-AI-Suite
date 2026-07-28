# SuperDev AI Suite - Makefile (Unix + PowerShell wrapper)
# Para Windows: use `make win-<comando>` ou leia Makefile.ps1

.PHONY: help install test lint format build run-api run-frontend clean

help:
	@echo "SuperDev AI Suite - Comandos"
	@echo ""
	@echo "  make install         - Instalar dependencias Python + Node"
	@echo "  make run-api         - Iniciar API (uvicorn)"
	@echo "  make run-frontend    - Iniciar frontend (Next.js)"
	@echo "  make test            - Rodar todos os testes"
	@echo "  make test-unit       - Testes unitarios Python"
	@echo "  make lint            - Lint Python (ruff)"
	@echo "  make format          - Format (ruff)"
	@echo "  make typecheck       - Type check (mypy)"
	@echo "  make migrate         - Rodar migrations"
	@echo "  make clean           - Limpar caches"
	@echo ""
	@echo "  make docker-build    - Build Docker"
	@echo "  make setup-dev       - Setup completo"

install:
	pip install -e ".[dev]"
	cd frontend && npm install

run-api:
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/runtime_engine/ -v

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy backend/

migrate:
	alembic upgrade head

docker-build:
	docker compose build

setup-dev: install migrate

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__
	rm -rf frontend/.next frontend/node_modules
	rm -rf .coverage *.egg-info

# ============================================================
# Comandos Windows (via PowerShell)
# ============================================================

.PHONY: win-install win-run-api win-run-frontend win-test win-clean

win-install:
	powershell -Command "pip install -e '.[dev]'; Set-Location frontend; npm install"

win-run-api:
	powershell -Command "uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

win-run-frontend:
	powershell -Command "Set-Location frontend; npm run dev"

win-test:
	powershell -Command "python -m pytest tests/ -v"

win-clean:
	powershell -Command "if (Test-Path '.pytest_cache') { Remove-Item -Recurse -Force '.pytest_cache' }; if (Test-Path '.ruff_cache') { Remove-Item -Recurse -Force '.ruff_cache' }; if (Test-Path '.next') { Remove-Item -Recurse -Force '.next' }; if (Test-Path 'node_modules') { Remove-Item -Recurse -Force 'node_modules' }"