# School Timetable - Makefile
# Usage: make <target>
# Run 'make help' to see all available commands

.DEFAULT_GOAL := help
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

# Variables
VENV := .venv/bin/activate
PYTHONPATH := PYTHONPATH=src
BACKEND_DIR := backend
WEB_DIR := web
DOCKER_COMPOSE := docker compose
DOCKER_COMPOSE_FILE := docker-compose.yml

# Colors for output
GREEN  := \033[32m
YELLOW := \033[33m
RED    := \033[31m
BLUE   := \033[34m
NC     := \033[0m

# =============================================================================
# HELP
# =============================================================================
.PHONY: help
help: ## Show this help
	@echo "$(BLUE)School Timetable - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# SETUP & INSTALL
# =============================================================================
.PHONY: setup setup-dev setup-frontend
setup: ## Create virtual environment and install all dependencies (dev + solver)
	python3 -m venv .venv
	. $(VENV) && pip install --upgrade pip
	. $(VENV) && pip install -e ".[dev,solver]"

setup-dev: setup ## Alias for setup
	@echo "$(GREEN)Development environment ready!$(NC)"

setup-frontend: ## Install frontend dependencies
	cd $(WEB_DIR) && npm ci

# =============================================================================
# DEVELOPMENT SERVERS
# =============================================================================
.PHONY: start stop restart status logs
start: ## Start all services (postgres, backend, frontend)
	@echo "$(BLUE)Starting all services...$(NC)"
	@if [ ! -f .env ] || ! grep -q '^SECRET_KEY=' .env; then \
		printf 'SECRET_KEY=%s\n' "$$(python3 -c 'import secrets; print(secrets.token_hex(32))')" >> .env; \
		echo "$(YELLOW)Generated .env with a random SECRET_KEY$(NC)"; \
	fi
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d --build
	@echo "$(GREEN)Services started!$(NC)"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API Docs: http://localhost:8000/docs"

stop: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down
	@echo "$(GREEN)Services stopped$(NC)"

restart: stop start ## Restart all services

status: ## Show status of all services
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps

logs: ## Follow logs of all services
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f --tail=100

logs-backend: ## Follow backend logs only
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f backend

logs-frontend: ## Follow frontend logs only
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f frontend

logs-db: ## Follow postgres logs only
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f postgres

# =============================================================================
# DEVELOPMENT SERVERS (without Docker)
# =============================================================================
.PHONY: run-backend run-frontend dev
run-backend: ## Start backend server locally (with hot reload)
	. $(VENV) && cd $(BACKEND_DIR) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Start frontend dev server locally
	cd $(WEB_DIR) && npm run dev

dev: ## Start both backend and frontend locally (requires tmux)
	@echo "$(YELLOW)Starting dev servers...$(NC)"
	@tmux new-session -d -s school-timetable 'make run-backend' \; \
		split-window -h 'make run-frontend' \; \
		attach-session -t school-timetable

# =============================================================================
# DATABASE OPERATIONS
# =============================================================================
.PHONY: db-migrate db-migrate-create db-reset db-seed db-shell db-backup db-restore
.PHONY: create-user create-admin
db-migrate: ## Run database migrations (Alembic)
	. $(VENV) && cd $(BACKEND_DIR) && alembic upgrade head

db-migrate-create: ## Create new migration (usage: make db-migrate-create msg="description")
	@if [ -z "$(msg)" ]; then echo "$(RED)Usage: make db-migrate-create msg=\"description\"$(NC)"; exit 1; fi
	. $(VENV) && cd $(BACKEND_DIR) && alembic revision --autogenerate -m "$(msg)"

db-migrate-history: ## Show migration history
	. $(VENV) && cd $(BACKEND_DIR) && alembic history

db-migrate-current: ## Show current migration
	. $(VENV) && cd $(BACKEND_DIR) && alembic current

db-downgrade: ## Downgrade one migration (usage: make db-downgrade rev=-1)
	. $(VENV) && cd $(BACKEND_DIR) && alembic downgrade $(rev)

db-reset: ## Reset database (drop all tables and re-run migrations)
	@echo "$(RED)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec postgres psql -U school -d school_timetable -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"; \
		. $(VENV) && cd $(BACKEND_DIR) && alembic upgrade head; \
		echo "$(GREEN)Database reset complete$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

db-seed: ## Seed database with demo accounts (admin/professor/aluno)
	@if $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps --status running -q backend 2>/dev/null | grep -q .; then \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec -T backend python -m scripts.seed; \
	else \
		. $(VENV) && cd $(BACKEND_DIR) && python -m scripts.seed; \
	fi

create-user: ## Create a user (usage: make create-user email=x role=admin [password=...])
	@if [ -z "$(email)" ]; then echo "usage: make create-user email=user@escola.pt role=admin [password=...] [name=...]"; exit 1; fi
	@if $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps --status running -q backend 2>/dev/null | grep -q .; then \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec -T backend python -m scripts.create_user --email "$(email)" --role "$(or $(role),student)" $(if $(password),--password "$(password)",) $(if $(name),--name "$(name)",); \
	else \
		. $(VENV) && cd $(BACKEND_DIR) && python -m scripts.create_user --email "$(email)" --role "$(or $(role),student)" $(if $(password),--password "$(password)",) $(if $(name),--name "$(name)",); \
	fi

create-admin: ## Create admin user quickly
	@if [ -z "$(email)" ]; then echo "usage: make create-admin email=admin@escola.pt [password=...]"; exit 1; fi
	@if $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps --status running -q backend 2>/dev/null | grep -q .; then \
		$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec -T backend python -m scripts.create_user --email "$(email)" --role admin $(if $(password),--password "$(password)",) $(if $(name),--name "$(name)",); \
	else \
		. $(VENV) && cd $(BACKEND_DIR) && python -m scripts.create_user --email "$(email)" --role admin $(if $(password),--password "$(password)",) $(if $(name),--name "$(name)",); \
	fi

db-shell: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec postgres psql -U school -d school_timetable

db-backup: ## Create database backup (usage: make db-backup file=backup.dump)
	@if [ -z "$(file)" ]; then file="backup_$$(date +%Y%m%d_%H%M%S).dump"; fi
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec -T postgres pg_dump -U school -d school_timetable -Fc > $(file)
	@echo "$(GREEN)Backup saved to $(file)$(NC)"

db-restore: ## Restore database from backup (usage: make db-restore file=backup.dump)
	@if [ -z "$(file)" ]; then echo "$(RED)Usage: make db-restore file=backup.dump$(NC)"; exit 1; fi
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec -T postgres pg_restore -U school -d school_timetable --clean --if-exists < $(file)
	@echo "$(GREEN)Database restored from $(file)$(NC)"

# =============================================================================
# TESTING
# =============================================================================
.PHONY: test test-unit test-integration test-e2e test-cov test-watch
test: ## Run all tests (unit + integration)
	. $(VENV) && PYTHONPATH=src python3 -m pytest tests/ -q -k "not test_cp_sat_dados_reais and not test_simulated_annealing_dados_reais and not test_tabu_search_dados_reais"

test-unit: ## Run unit tests only
	. $(VENV) && PYTHONPATH=src python3 -m pytest tests/ -q -k "unit"

test-integration: ## Run integration tests only
	. $(VENV) && PYTHONPATH=src python3 -m pytest tests/ -q -k "integration"

test-e2e: ## Run E2E tests (requires full stack: make start)
	FULL_STACK_E2E=1 npx playwright test --project=chromium

test-e2e-headed: ## Run E2E tests with browser visible
	FULL_STACK_E2E=1 npx playwright test --project=chromium --headed

test-e2e-debug: ## Run E2E tests in debug mode
	FULL_STACK_E2E=1 npx playwright test --project=chromium --debug

test-cov: ## Run tests with coverage report
	. $(VENV) && PYTHONPATH=src python3 -m pytest tests/ --cov=src/timetable --cov-report=html --cov-report=term-missing

test-watch: ## Run tests in watch mode
	. $(VENV) && PYTHONPATH=src python3 -m pytest tests/ -f --watch

test-backend: ## Run backend tests only
	cd $(BACKEND_DIR) && PYTHONPATH=. python3 -m pytest tests/ -q

test-frontend: ## Run frontend tests only
	cd $(WEB_DIR) && npm test

test-all: test test-frontend ## Run all tests (backend + frontend)

# =============================================================================
# CODE QUALITY
# =============================================================================
.PHONY: lint lint-fix fmt typecheck security
lint: ## Run linters (ruff + mypy)
	. $(VENV) && ruff check src tests backend/app backend/tests
	. $(VENV) && mypy src backend/app

lint-fix: ## Auto-fix linting issues
	. $(VENV) && ruff check --fix src tests backend/app backend/tests

fmt: ## Format code with ruff
	. $(VENV) && ruff format src tests backend/app backend/tests

typecheck: ## Run type checking with mypy
	. $(VENV) && mypy src backend/app

security: ## Security audit
	. $(VENV) && pip-audit
	cd $(WEB_DIR) && npm audit

# =============================================================================
# BUILD & DEPLOY
# =============================================================================
.PHONY: build build-backend build-frontend build-docker push-docker deploy-staging deploy-prod
build: build-backend build-frontend ## Build all Docker images

build-backend: ## Build backend Docker image
	docker build -t school-timetable-backend:latest -f $(BACKEND_DIR)/docker/Dockerfile.backend .

build-frontend: ## Build frontend Docker image
	docker build -t school-timetable-frontend:latest -f $(WEB_DIR)/docker/Dockerfile.frontend .

build-docker: ## Build all Docker images
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) build --no-cache

push-docker: ## Push Docker images to registry (usage: make push-docker tag=v1.0.0)
	@if [ -z "$(tag)" ]; then echo "$(RED)Usage: make push-docker tag=v1.0.0$(NC)"; exit 1; fi
	docker tag school-timetable-backend:latest $$(REGISTRY)/school-timetable-backend:$(tag)
	docker tag school-timetable-frontend:latest $$(REGISTRY)/school-timetable-frontend:$(tag)
	docker push $$(REGISTRY)/school-timetable-backend:$(tag)
	docker push $$(REGISTRY)/school-timetable-frontend:$(tag)

deploy-staging: ## Deploy to staging (placeholder)
	@echo "$(YELLOW)Deploy to staging - implement your deployment logic$(NC)"

deploy-prod: ## Deploy to production (placeholder)
	@echo "$(YELLOW)Deploy to production - implement your deployment logic$(NC)"

# =============================================================================
# UTILITIES
# =============================================================================
.PHONY: clean tree shell shell-backend shell-frontend shell-db version
clean: ## Remove build artifacts, cache, and virtual environment
	rm -rf .venv build dist *.egg-info src/*.egg-info .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	cd $(WEB_DIR) && rm -rf node_modules/.vite dist 2>/dev/null || true

tree: ## Show project structure (excluding .venv, .git, node_modules)
	find . -type f -not -path './.venv/*' -not -path './.git/*' -not -path './node_modules/*' -not -path './web/node_modules/*' | sort

shell: ## Open Python shell with project context
	. $(VENV) && python3 -c "import sys; sys.path.insert(0, 'src'); import timetable; print('Ready!')"

shell-backend: ## Open Python shell with backend context
	. $(VENV) && cd $(BACKEND_DIR) && python3 -c "import sys; sys.path.insert(0, '..'); from app.db.session import AsyncSessionLocal; print('Backend shell ready')"

shell-frontend: ## Open Node REPL with frontend context
	cd $(WEB_DIR) && node

shell-db: ## Open PostgreSQL shell
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec postgres psql -U school -d school_timetable

version: ## Show project version
	@python3 -c "import toml; data=toml.load('pyproject.toml'); print(data['project']['version'])"

# =============================================================================
# CI/CD HELPERS
# =============================================================================
.PHONY: ci-test ci-lint ci-build
ci-test: ## Run tests in CI mode
	. $(VENV) && PYTHONPATH=src python3 -m pytest tests/ -q -k "not test_cp_sat_dados_reais and not test_simulated_annealing_dados_reais and not test_tabu_search_dados_reais" --cov=src/timetable --cov-report=xml --cov-fail-under=80

ci-lint: ## Run linters in CI mode
	. $(VENV) && ruff check src tests backend/app backend/tests --output-format=github
	. $(VENV) && mypy src backend/app --strict

ci-build: ## Build in CI mode
	docker build -t school-timetable-backend:ci -f $(BACKEND_DIR)/docker/Dockerfile.backend $(BACKEND_DIR)
	docker build -t school-timetable-frontend:ci -f $(WEB_DIR)/docker/Dockerfile.frontend $(WEB_DIR)

# =============================================================================
# QUICK COMMANDS
# =============================================================================
.PHONY: quick-start quick-test quick-lint
quick-start: setup ## Quick start: setup + start services
	make start

quick-test: lint test ## Quick validation: lint + test

quick-lint: lint-fix fmt ## Quick lint fix

# =============================================================================
# MONITORING & DEBUG
# =============================================================================
.PHONY: health-check perf-profile
health-check: ## Check health of all services
	@echo "$(BLUE)Checking services...$(NC)"
	@curl -sf http://localhost:8000/health > /dev/null && echo "$(GREEN)✓ Backend OK$(NC)" || echo "$(RED)✗ Backend FAIL$(NC)"
	@curl -sf http://localhost:3000 > /dev/null && echo "$(GREEN)✓ Frontend OK$(NC)" || echo "$(RED)✗ Frontend FAIL$(NC)"
	@$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec postgres pg_isready -U school -d school_timetable && echo "$(GREEN)✓ Database OK$(NC)" || echo "$(RED)✗ Database FAIL$(NC)"

perf-profile: ## Profile backend performance (requires py-spy)
	. $(VENV) && pip install py-spy
	sudo py-spy record -o profile.svg -- python -m pytest tests/ -q

# =============================================================================
# DEFAULT
# =============================================================================
.DEFAULT_GOAL := help