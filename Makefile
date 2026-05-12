# ============================================================
# In-The-Life — Makefile (25 Targets)
# Usage: make help
# ============================================================
.PHONY: help build up down logs ps restart
.PHONY: migrate migrate-down migrate-new seed db-shell
.PHONY: test test-backend test-frontend test-cov test-e2e
.PHONY: lint format type-check quality
.PHONY: docker-build docker-push deploy rollback
.PHONY: backup restore clean

SHELL := /bin/bash
DC    := docker compose
DCP   := docker compose -f docker-compose.prod.yml

help:  ## Show all targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Development -------------------------------------------
build:  ## Build all Docker images (dev)
	$(DC) build --parallel

up:  ## Start dev stack
	$(DC) up -d
	@echo "\n✅ Stack running → API: http://localhost:8000/docs | Frontend: http://localhost:3000"

down:  ## Stop dev stack
	$(DC) down

logs:  ## Follow all logs
	$(DC) logs -f

logs-backend:  ## Follow backend logs
	$(DC) logs -f backend

ps:  ## Container status
	$(DC) ps

restart:  ## Restart services
	$(DC) restart

# --- Database ----------------------------------------------
migrate:  ## Run alembic upgrade head
	cd backend && alembic upgrade head

migrate-down:  ## Run alembic downgrade -1
	cd backend && alembic downgrade -1

migrate-new:  ## Create new migration (m="description")
	cd backend && alembic revision --autogenerate -m "$(m)"

seed:  ## Seed geo data (continents + countries)
	cd backend && python -m scripts.seed_data

db-shell:  ## Open PostgreSQL shell
	$(DC) exec postgres psql -U itl_user in_the_life

# --- Tests -------------------------------------------------
test:  ## Run all tests
	$(MAKE) test-backend
	$(MAKE) test-frontend

test-backend:  ## Run backend tests (pytest)
	cd backend && pytest tests/ -v --tb=short

test-frontend:  ## Run frontend tests (vitest)
	cd frontend && npm test -- --run

test-cov:  ## Backend tests with coverage report
	cd backend && pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
	@echo "\n📊 Coverage: backend/htmlcov/index.html"

test-e2e:  ## E2E tests (Playwright)
	cd frontend && npx playwright test

# --- Code Quality ------------------------------------------
lint:  ## Ruff + ESLint
	cd backend && ruff check app tests
	cd frontend && npx eslint src --ext ts,tsx

format:  ## Ruff format + Prettier
	cd backend && ruff format app tests
	cd frontend && npx prettier --write src

type-check:  ## mypy + TypeScript
	cd backend && mypy app --ignore-missing-imports
	cd frontend && npx tsc --noEmit

quality:  ## All quality checks
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test-cov

# --- Docker / Deploy ---------------------------------------
docker-build:  ## Build production images
	$(DCP) build --parallel

docker-push:  ## Push images to GHCR
	docker push ghcr.io/$${GITHUB_REPO}/backend:latest
	docker push ghcr.io/$${GITHUB_REPO}/worker:latest
	docker push ghcr.io/$${GITHUB_REPO}/frontend:latest

deploy:  ## Production deployment
	$(DCP) pull
	$(DCP) up -d --no-build

rollback:  ## Rollback last deployment
	kubectl rollout undo deployment/backend  -n in-the-life
	kubectl rollout undo deployment/worker   -n in-the-life
	kubectl rollout undo deployment/frontend -n in-the-life

# --- Maintenance -------------------------------------------
backup:  ## Database backup
	@mkdir -p backups
	docker exec $$($(DC) ps -q postgres) \
	  pg_dump -U itl_user in_the_life | gzip > backups/itl_$$(date +%Y%m%d_%H%M%S).sql.gz
	@echo "✅ Backup saved to backups/"

restore:  ## Database restore (f=backup_file.sql.gz)
	gunzip -c $(f) | docker exec -i $$($(DC) ps -q postgres) psql -U itl_user in_the_life

clean:  ## Remove containers + volumes (CAUTION!)
	$(DC) down -v --remove-orphans
	docker system prune -f
