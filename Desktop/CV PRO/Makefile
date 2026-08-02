.PHONY: help setup up down logs backend frontend test clean lint format

help:
	@echo "CareerOS AI Development Commands"
	@echo "================================="
	@echo "make setup           - Setup development environment"
	@echo "make up              - Start all services"
	@echo "make down            - Stop all services"
	@echo "make logs            - View logs (all services)"
	@echo "make backend-logs    - View backend logs only"
	@echo "make frontend-logs   - View frontend logs only"
	@echo "make backend         - Start backend only"
	@echo "make frontend        - Start frontend only"
	@echo "make db-migrate      - Run database migrations"
	@echo "make db-seed         - Seed database with test data"
	@echo "make test            - Run all tests"
	@echo "make test-backend    - Run backend tests"
	@echo "make test-frontend   - Run frontend tests"
	@echo "make lint            - Run linters (black, flake8, mypy, eslint)"
	@echo "make format          - Auto-format code (black, prettier)"
	@echo "make clean           - Remove containers and volumes"
	@echo "make shell-db        - Connect to PostgreSQL shell"
	@echo "make shell-redis     - Connect to Redis CLI"

setup:
	@echo "Setting up development environment..."
	cp backend/.env.example backend/.env
	@echo "✓ Created backend/.env"
	docker-compose build
	@echo "✓ Docker images built"
	docker-compose up -d postgres redis
	sleep 5
	docker-compose run --rm backend alembic upgrade head
	@echo "✓ Database migrations complete"
	@echo ""
	@echo "Setup complete! Run 'make up' to start all services."

up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo "✓ Services started"
	@echo ""
	@echo "Services running:"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Frontend: http://localhost:3000 (if running locally)"
	@echo "  Database: localhost:5432"
	@echo "  Redis:    localhost:6379"
	@echo "  Nginx:    http://localhost:80"

down:
	@echo "Stopping all services..."
	docker-compose down
	@echo "✓ Services stopped"

logs:
	docker-compose logs -f

backend-logs:
	docker-compose logs -f backend

frontend-logs:
	docker-compose logs -f frontend

celery-logs:
	docker-compose logs -f celery

backend:
	@echo "Starting backend service..."
	docker-compose up backend

frontend:
	@echo "Starting frontend service..."
	cd frontend && npm install && npm run dev

db-migrate:
	@echo "Running database migrations..."
	docker-compose run --rm backend alembic upgrade head
	@echo "✓ Migrations complete"

db-seed:
	@echo "Seeding database with test data..."
	docker-compose run --rm backend python scripts/seed.py
	@echo "✓ Database seeded"

db-rollback:
	@echo "Rolling back last migration..."
	docker-compose run --rm backend alembic downgrade -1
	@echo "✓ Rollback complete"

test:
	@echo "Running all tests..."
	make test-backend
	make test-frontend

test-backend:
	@echo "Running backend tests..."
	docker-compose run --rm backend pytest --cov=app tests/ -v
	@echo "✓ Backend tests complete"

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test -- --coverage
	@echo "✓ Frontend tests complete"

lint:
	@echo "Running linters..."
	@echo "Backend:"
	docker-compose run --rm backend flake8 app --max-line-length=100
	docker-compose run --rm backend mypy app --strict
	@echo "✓ Backend lint complete"
	@echo ""
	@echo "Frontend:"
	cd frontend && npm run lint
	@echo "✓ Frontend lint complete"

format:
	@echo "Auto-formatting code..."
	@echo "Backend:"
	docker-compose run --rm backend black app tests --line-length=100
	docker-compose run --rm backend isort app tests
	@echo "✓ Backend formatted"
	@echo ""
	@echo "Frontend:"
	cd frontend && npm run format
	@echo "✓ Frontend formatted"

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name node_modules -exec rm -rf {} +
	find . -name ".DS_Store" -delete
	@echo "✓ Clean complete"

shell-db:
	docker-compose exec postgres psql -U careeeros -d careeeros_ai

shell-redis:
	docker-compose exec redis redis-cli

shell-backend:
	docker-compose exec backend /bin/bash

shell-frontend:
	cd frontend && bash

install-frontend:
	cd frontend && npm install

install-backend:
	pip install -r backend/requirements.txt

# CI/CD helpers
ci-lint: lint
ci-test: test
ci-build:
	docker-compose build
	@echo "✓ Images built"

# Production commands (use with care!)
prod-migrate:
	@echo "WARNING: Running migrations in production"
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose -f docker-compose.prod.yml run --rm backend alembic upgrade head; \
	fi

prod-backup:
	@echo "Backing up production database..."
	docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U careeeros -d careeeros_ai > backup-$$(date +%Y%m%d-%H%M%S).sql
	@echo "✓ Backup complete"

.DEFAULT_GOAL := help
