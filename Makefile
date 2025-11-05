PODMAN_COMPOSE = podman-compose
PODMAN_COMPOSE_FILE = podman-compose.yml

.PHONY: build up down restart logs test clean

help:
	@echo "Available commands:"
	@echo "  make makemigration desc='msg'   - Create new migration"
	@echo "  make migrate                           - Apply all migrations"
	@echo "  make up                                - Start services"
	@echo "  make down                              - Stop services"
	@echo "  make restart                           - Restart services"
	@echo "  make logs                              - Show logs"
	@echo "  make clean                             - Remove unused Docker data"
	@echo "  make setup                             - Setup project (venv, deps, pre-commit, migrations)"
	@echo "  make run                               - Run FastAPI with uvicorn"
	@echo "  make pycache                           - Remove __pycache__ and *.pyc files"
	@echo "  make test                              - Run all tests"
	@echo "  make test-matching K=pattern           - Run tests matching keyword pattern"
	@echo "  make coverage                          - Run tests with coverage"
	@echo "  make lint                              - Run lint checks"
	@echo "  make lintfix                          - Run lint checks and auto-fix + format"


.env: .example.env
	@cp .example.env .env || echo "NOTE: review your .env file comparing with .example.env"
	@touch .env

up:
	@echo "Starting services..."
	$(PODMAN_COMPOSE) -f $(PODMAN_COMPOSE_FILE) up -d

down:
	@echo "Stopping services..."
	$(PODMAN_COMPOSE) -f $(PODMAN_COMPOSE_FILE) down

restart: down up

logs:
	@echo "Showing logs..."
	$(PODMAN_COMPOSE) -f $(PODMAN_COMPOSE_FILE) logs -f

clean:
	@echo "Cleaning up..."
	podman system prune -a --volumes -f

setup:
	@echo "Setting up project..."
	@uv sync
	@uv run pre-commit install
	@uv run alembic upgrade head
	@echo "Setup Completed"

run:
	@uv run python -m app.main

cache:
	@echo "Cleaning all cached files..."
	@find . \( -name *.py[co] -o -name __pycache__ \) -delete
	@rm -rf .ruff_cache
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@echo "Done."


migrate:
	@PYTHONPATH=$PYTHONPATH:$(pwd) uv run alembic upgrade head

makemigration:
	@PYTHONPATH=$PYTHONPATH:$(pwd) uv run alembic revision --autogenerate -m $(desc)

test:
	@uv run pytest

test-coverage:
	@uv run pytest --cov=app --cov-report=term-missing --cov-report=html
	@rm -f .coverage
	@xdg-open htmlcov/index.html # if you want to open in the browser automatically

test-matching:
	@uv run pytest -vv -k $(N)

test-suite:
	@uv run pytest --cov=app --cov-report=term-missing --cov-report=html
	@rm -f .coverage
	@xdg-open htmlcov/index.html # if you want to open in the browser automatically

.PHONY: run test generate-coverage lint-check lint-fix
