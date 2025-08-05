.PHONY: install-backend install-frontend install run-backend run-frontend dev setup build up down logs clean

install-backend:
	cd backend && python3 -m venv .venv && .venv/bin/pip install --upgrade pip && .venv/bin/pip install -r requirements.txt

install-frontend:
	cd frontend && npm install

install: install-backend install-frontend

run-backend:
	cd backend && .venv/bin/python app.py

run-frontend:
	cd frontend && npm run dev

setup:
	@echo "🚀 Setting up MAG7 Stock Returns Dashboard..."
	@echo "📦 Installing backend dependencies..."
	@cd backend && if [ ! -d ".venv" ]; then python3 -m venv .venv; fi
	@cd backend && .venv/bin/pip install --upgrade pip > /dev/null 2>&1 || true
	@cd backend && .venv/bin/pip install -r requirements.txt > /dev/null 2>&1 || true
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && if [ ! -d "node_modules" ]; then npm install > /dev/null 2>&1; fi
	@echo "✅ Setup complete!"

dev: setup
	@echo "🚀 Starting MAG7 Stock Returns Dashboard..."
	@echo "📊 Backend API will be available at http://localhost:8000"
	@echo "🌐 Frontend will be available at http://localhost:3000"
	@echo "🔥 Starting both services..."
	@make -j2 run-backend run-frontend

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

kill:
	@echo "Stopping all services..."
	@pkill -f "python app.py" || true
	@pkill -f "npm run dev" || true
	@pkill -f "vite" || true
	@echo "✓ All services stopped"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf frontend/node_modules
	rm -rf frontend/dist
	rm -rf backend/.venv