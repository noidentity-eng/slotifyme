.PHONY: help install test lint format clean docker-build docker-run migrate seed

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=tenant --cov-report=html --cov-report=term-missing

lint: ## Run linting
	ruff check tenant/
	mypy tenant/

format: ## Format code
	black tenant/
	ruff check --fix tenant/

clean: ## Clean up generated files
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage

docker-build: ## Build Docker image
	docker build -t tenant-service .

docker-run: ## Run with Docker Compose
	docker-compose up -d

docker-stop: ## Stop Docker Compose
	docker-compose down

migrate: ## Run database migrations
	alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MESSAGE="description")
	alembic revision --autogenerate -m "$(MESSAGE)"

seed: ## Seed database with initial data
	python scripts/init_db.py

dev: ## Start development environment
	docker-compose up -d postgres redis
	sleep 5
	alembic upgrade head
	python scripts/init_db.py
	uvicorn tenant.app.main:app --reload

all: install format lint test ## Run all checks
