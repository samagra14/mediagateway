.PHONY: help setup dev dev-backend dev-frontend docker-up docker-down docker-logs docker-build clean

help:
	@echo "MediaRouter - Available Commands:"
	@echo "  make setup         - Run initial setup"
	@echo "  make dev           - Run both backend and frontend in dev mode"
	@echo "  make dev-backend   - Run only backend"
	@echo "  make dev-frontend  - Run only frontend"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-logs   - View Docker logs"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make clean         - Clean up generated files"

setup:
	@./setup.sh

dev:
	@echo "Starting development servers..."
	@trap 'kill 0' INT; \
	cd backend && python run.py & \
	cd frontend && npm run dev & \
	wait

dev-backend:
	@cd backend && python run.py

dev-frontend:
	@cd frontend && npm run dev

docker-up:
	@docker-compose up -d
	@echo "✅ Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:3001"

docker-down:
	@docker-compose down

docker-logs:
	@docker-compose logs -f

docker-build:
	@docker-compose build

clean:
	@echo "Cleaning up..."
	@rm -rf backend/__pycache__
	@rm -rf backend/src/__pycache__
	@rm -rf backend/.pytest_cache
	@rm -rf frontend/dist
	@rm -rf frontend/node_modules/.vite
	@rm -rf storage/*.sqlite
	@echo "✅ Cleanup complete"
