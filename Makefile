VENV        := backend/venv
PYTHON      := $(VENV)/bin/python
PIP         := $(VENV)/bin/pip
UVICORN     := $(VENV)/bin/uvicorn
ALEMBIC     := $(VENV)/bin/alembic

.PHONY: install dev build migrate deploy logs test lint clean

install: ## Install all dependencies (Python + Node)
	python3.11 -m venv $(VENV) && $(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt
	cd frontend && npm ci

dev: ## Start backend (hot-reload) + frontend (Vite dev server) in parallel
	@trap 'kill %1 %2 2>/dev/null; exit' INT; \
	cd backend && $(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload & \
	cd frontend && npm run dev & \
	wait

dev-backend: ## Start backend only with hot-reload
	cd backend && $(UVICORN) app.main:app --host 0.0.0.0 --port 8000 --reload

dev-bot: ## Start Telegram bot only
	cd backend && $(PYTHON) -m app.modules.bot.run_bot

build: ## Build React frontend for production
	cd frontend && npm run build

migrate: ## Run Alembic migrations (upgrade head)
	cd backend && $(ALEMBIC) upgrade head

migrate-down: ## Rollback last migration
	cd backend && $(ALEMBIC) downgrade -1

migrate-new: ## Create a new Alembic migration (use: make migrate-new MSG="description")
	cd backend && $(ALEMBIC) revision --autogenerate -m "$(MSG)"

deploy: build ## Build frontend then restart all PM2 processes
	pm2 restart all

deploy-backend: ## Restart backend only
	pm2 restart immosure-backend

deploy-bot: ## Restart bot only
	pm2 restart immosure-bot

logs: ## Tail all PM2 logs
	pm2 logs

logs-backend: ## Tail backend logs only
	pm2 logs immosure-backend

logs-bot: ## Tail bot logs only
	pm2 logs immosure-bot

status: ## Show PM2 process status
	pm2 status

test: ## Run backend tests
	cd backend && $(PYTHON) -m pytest tests/ -v

lint: ## Lint Python code with ruff
	cd backend && $(VENV)/bin/ruff check app/

clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null; true
	rm -rf frontend/dist frontend/node_modules/.cache 2>/dev/null; true

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
