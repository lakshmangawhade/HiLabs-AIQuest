# HiLabs Docker Makefile
# Simplifies Docker commands for development and deployment

.PHONY: help build up down restart logs shell test clean

# Default target
help:
	@echo "HiLabs Docker Management Commands:"
	@echo ""
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View service logs"
	@echo "  make shell-back  - Access backend shell"
	@echo "  make shell-front - Access frontend shell"
	@echo "  make test        - Run deployment test"
	@echo "  make clean       - Clean up everything"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev         - Start in development mode"
	@echo "  make dev-logs    - View development logs"
	@echo "  make dev-down    - Stop development services"
	@echo ""

# Build Docker images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d --build

# Stop services
down:
	docker-compose down

# Restart services
restart:
	docker-compose down
	docker-compose up -d --build

# View logs
logs:
	docker-compose logs -f

# Access backend shell
shell-back:
	docker-compose exec backend bash

# Access frontend shell
shell-front:
	docker-compose exec frontend sh

# Run test script
test:
	@if [ -f docker-test.sh ]; then \
		bash docker-test.sh; \
	elif [ -f docker-test.bat ]; then \
		cmd //c docker-test.bat; \
	else \
		echo "Test script not found"; \
	fi

# Clean everything
clean:
	docker-compose down -v
	docker system prune -af

# Development mode
dev:
	docker-compose -f docker-compose.dev.yml up --build

# Development logs
dev-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Stop development
dev-down:
	docker-compose -f docker-compose.dev.yml down

# Production deployment
prod:
	docker-compose -f docker-compose.yml up -d --build

# Check health
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | python -m json.tool || echo "Backend not responding"
	@curl -s -o /dev/null -w "Frontend HTTP Status: %{http_code}\n" http://localhost:3000 || echo "Frontend not responding"

# Backup data
backup:
	@echo "Creating backup..."
	@mkdir -p backups
	@docker run --rm -v hilabs-aiquest_uploads:/data -v $(PWD)/backups:/backup alpine tar czf /backup/uploads_$(shell date +%Y%m%d_%H%M%S).tar.gz -C /data .
	@docker run --rm -v hilabs-aiquest_results:/data -v $(PWD)/backups:/backup alpine tar czf /backup/results_$(shell date +%Y%m%d_%H%M%S).tar.gz -C /data .
	@echo "Backup completed in ./backups/"
