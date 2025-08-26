# Dedyfo Bot - Professional Development Makefile

.PHONY: help install dev run test lint format clean docker docker-dev docker-prod logs backup restore

# Variables
PYTHON := python3.11
PIP := pip
COMPOSE := docker-compose
PROJECT_NAME := dedyfo-bot

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default target
help: ## Show this help message
	@echo "$(GREEN)Dedyfo Bot - Development Commands$(NC)"
	@echo "=================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development Setup
install: ## Install development dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

dev: ## Setup development environment
	@echo "$(GREEN)Setting up development environment...$(NC)"
	$(PIP) install -r requirements.txt
	cp env.example .env
	@echo "$(YELLOW)Please edit .env file with your configuration$(NC)"
	@echo "$(GREEN)Development environment ready!$(NC)"

# Running
run: ## Run bot in development mode
	@echo "$(GREEN)Starting bot...$(NC)"
	$(PYTHON) main.py

run-webhook: ## Run bot in webhook mode
	@echo "$(GREEN)Starting bot in webhook mode...$(NC)"
	WEBHOOK_URL=https://yourdomain.com $(PYTHON) main.py

# Code Quality
test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	pytest tests/ -v --cov=bot --cov-report=html --cov-report=term

test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	pytest-watch

lint: ## Run linting
	@echo "$(GREEN)Running linting...$(NC)"
	flake8 bot/ main.py
	mypy bot/ main.py

format: ## Format code
	@echo "$(GREEN)Formatting code...$(NC)"
	black bot/ main.py
	@echo "$(GREEN)Code formatted!$(NC)"

check: lint test ## Run all checks (lint + test)

# Docker Commands
docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t $(PROJECT_NAME):latest .

docker-dev: ## Run development environment with Docker
	@echo "$(GREEN)Starting development environment...$(NC)"
	$(COMPOSE) -f docker-compose.yml up --build

docker-prod: ## Run production environment with Docker
	@echo "$(GREEN)Starting production environment...$(NC)"
	$(COMPOSE) -f docker-compose.yml --profile production up -d

docker-stop: ## Stop Docker containers
	@echo "$(GREEN)Stopping containers...$(NC)"
	$(COMPOSE) down

docker-logs: ## Show Docker logs
	$(COMPOSE) logs -f bot

docker-shell: ## Access bot container shell
	$(COMPOSE) exec bot /bin/bash

# Database Commands
db-upgrade: ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(NC)"
	$(COMPOSE) run --rm migrations

db-downgrade: ## Downgrade database
	@echo "$(YELLOW)Downgrading database...$(NC)"
	$(COMPOSE) run --rm bot python -m alembic downgrade -1

db-reset: ## Reset database (DANGEROUS)
	@echo "$(RED)Resetting database...$(NC)"
	$(COMPOSE) down -v
	$(COMPOSE) up postgres -d
	sleep 5
	$(COMPOSE) run --rm migrations

# Monitoring
logs: ## Show application logs
	tail -f logs/bot.log

logs-docker: docker-logs ## Show Docker logs (alias)

monitoring: ## Start monitoring stack
	@echo "$(GREEN)Starting monitoring stack...$(NC)"
	$(COMPOSE) --profile monitoring up -d prometheus grafana

# Backup & Restore
backup: ## Backup database
	@echo "$(GREEN)Creating database backup...$(NC)"
	$(COMPOSE) exec postgres pg_dump -U postgres dedyfo_bot > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup created!$(NC)"

restore: ## Restore database from backup (provide BACKUP_FILE=filename)
	@echo "$(YELLOW)Restoring database from $(BACKUP_FILE)...$(NC)"
	$(COMPOSE) exec -T postgres psql -U postgres dedyfo_bot < $(BACKUP_FILE)
	@echo "$(GREEN)Database restored!$(NC)"

# Cleaning
clean: ## Clean up temporary files
	@echo "$(GREEN)Cleaning up...$(NC)"
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	@echo "$(GREEN)Cleanup complete!$(NC)"

clean-docker: ## Clean up Docker resources
	@echo "$(GREEN)Cleaning up Docker resources...$(NC)"
	$(COMPOSE) down --volumes --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Docker cleanup complete!$(NC)"

# Deployment
deploy-staging: ## Deploy to staging environment
	@echo "$(GREEN)Deploying to staging...$(NC)"
	# Add your staging deployment commands here

deploy-prod: ## Deploy to production environment
	@echo "$(GREEN)Deploying to production...$(NC)"
	# Add your production deployment commands here

# Security
security-check: ## Run security checks
	@echo "$(GREEN)Running security checks...$(NC)"
	pip-audit
	bandit -r bot/

# Development Utilities
create-migration: ## Create new database migration (provide NAME=migration_name)
	@echo "$(GREEN)Creating migration: $(NAME)$(NC)"
	$(COMPOSE) run --rm bot alembic revision --autogenerate -m "$(NAME)"

shell: ## Start Python shell with app context
	@echo "$(GREEN)Starting Python shell...$(NC)"
	$(PYTHON) -c "from bot import *; import asyncio"

# Quick start for new developers
quick-start: dev docker-build ## Quick setup for new developers
	@echo "$(GREEN)Quick start complete!$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "1. Edit .env file with your bot token"
	@echo "2. Run 'make docker-dev' to start development environment"
	@echo "3. Run 'make test' to verify everything works"

# Show project status
status: ## Show project status
	@echo "$(GREEN)Project Status$(NC)"
	@echo "=============="
	@echo "Python version: $(shell python --version)"
	@echo "Bot version: $(shell grep version pyproject.toml | head -1 | cut -d'"' -f2)"
	@echo "Docker status: $(shell docker --version 2>/dev/null || echo 'Not installed')"
	@echo "Compose status: $(shell docker-compose --version 2>/dev/null || echo 'Not installed')"
