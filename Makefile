.PHONY: help install setup-db run-once run-scheduler docker-up docker-down test lint format clean

help:
	@echo "Job Tracker - Available Commands"
	@echo "================================="
	@echo "install         - Install dependencies with Poetry"
	@echo "setup-db        - Initialize database with migrations"
	@echo "run-once        - Run tracker once (no scheduling)"
	@echo "run-scheduler   - Run with APScheduler (local)"
	@echo "docker-up       - Start all services with Docker Compose"
	@echo "docker-down     - Stop all Docker services"
	@echo "test            - Run tests"
	@echo "lint            - Run linting checks"
	@echo "format          - Format code with Black"
	@echo "clean           - Clean temporary files"

install:
	poetry install

setup-db:
	poetry run alembic upgrade head

run-once:
	poetry run python -m src.ingest.runner

run-scheduler:
	poetry run python -m src.scheduler.apscheduler_runner

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

test:
	poetry run pytest tests/ -v

lint:
	poetry run ruff check src/
	poetry run mypy src/

format:
	poetry run black src/
	poetry run ruff check --fix src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
