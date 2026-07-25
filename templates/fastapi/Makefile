.PHONY: install dev test lint format run docker

install:
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload

test:
	pytest tests/ -v

lint:
	ruff check app/

format:
	ruff format app/

run: docker

docker:
	docker-compose up --build
