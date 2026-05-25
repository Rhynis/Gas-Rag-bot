.PHONY: help setup dev test lint format clean migrate seed docker-up docker-down

help:
	@echo "GasBot Vietnam — Available commands:"
	@echo "  make setup       — One-command development setup"
	@echo "  make dev         — Start both frontend and backend in dev mode"
	@echo "  make test        — Run all tests (frontend + backend)"
	@echo "  make lint        — Run all linters"
	@echo "  make format      — Auto-format all code"
	@echo "  make clean       — Remove generated files and caches"
	@echo "  make migrate     — Run database migrations"
	@echo "  make seed        — Load seed data"
	@echo "  make docker-up   — Start Docker services"
	@echo "  make docker-down — Stop Docker services"

setup:
	./scripts/setup.sh

dev:
	@echo "Starting backend and frontend..."
	(cd backend && uvicorn app.main:app --reload --port 8000) &
	(cd frontend && npm run dev) &
	wait

test:
	./scripts/test-all.sh

lint:
	cd backend && ruff check . && mypy app/
	cd frontend && npm run lint && npm run type-check

format:
	cd backend && ruff format .
	cd frontend && npm run format

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
	find . -type d -name .next -exec rm -rf {} +
	rm -rf backend/htmlcov backend/.coverage

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m scripts.seed_data

docker-up:
	docker compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 5
	docker compose ps

docker-down:
	docker compose down
