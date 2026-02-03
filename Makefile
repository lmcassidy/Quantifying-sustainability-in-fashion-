.PHONY: install install-backend install-frontend dev dev-backend dev-frontend build train-model test clean

# Install all dependencies
install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	pip install -e .
	pip install -r backend/requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Development servers
dev-backend:
	@echo "Starting backend server..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend server..."
	cd frontend && npm run dev

# Run both servers (requires 'make dev-backend' in another terminal, or use concurrently)
dev:
	@echo "Run 'make dev-backend' and 'make dev-frontend' in separate terminals"
	@echo "Or install concurrently: npm install -g concurrently"
	@echo "Then run: concurrently \"make dev-backend\" \"make dev-frontend\""

# Build frontend for production
build:
	cd frontend && npm run build

# Train the price prediction model
train-model:
	@echo "Training price prediction model..."
	cd backend && python train_model.py

# Run tests
test:
	@echo "Running backend tests..."
	PYTHONPATH=src python -m pytest tests/ -v

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf frontend/dist
	rm -rf backend/models/*.joblib
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Help
help:
	@echo "Available commands:"
	@echo "  make install          - Install all dependencies"
	@echo "  make dev-backend      - Start FastAPI server (port 8000)"
	@echo "  make dev-frontend     - Start Vite dev server (port 5173)"
	@echo "  make build            - Build frontend for production"
	@echo "  make train-model      - Train and save price prediction model"
	@echo "  make test             - Run backend tests"
	@echo "  make clean            - Remove build artifacts"
