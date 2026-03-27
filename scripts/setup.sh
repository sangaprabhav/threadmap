#!/usr/bin/env bash
# ThreadMap — Development Setup Script
set -euo pipefail

echo "=== ThreadMap Development Setup ==="

# 1. Start infrastructure
echo "[1/5] Starting infrastructure (Docker Compose)..."
cd infrastructure
docker compose up -d
cd ..

# 2. Wait for services
echo "[2/5] Waiting for services..."
sleep 5
until docker compose -f infrastructure/docker-compose.yml exec -T postgres pg_isready -U threadmap 2>/dev/null; do
    echo "  Waiting for PostgreSQL..."
    sleep 2
done
echo "  PostgreSQL ready."

# 3. Backend setup
echo "[3/5] Setting up Python backend..."
cd src/backend
python -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -e ".[dev]" --quiet
python -m spacy download en_core_web_sm --quiet 2>/dev/null || echo "  Note: spacy model download may require manual: python -m spacy download en_core_web_sm"

# 4. Run migrations
echo "[4/5] Running database migrations..."
alembic upgrade head 2>/dev/null || echo "  Note: Run 'alembic revision --autogenerate -m initial' then 'alembic upgrade head'"
cd ../..

# 5. Frontend setup
echo "[5/5] Setting up Next.js frontend..."
cd src/frontend
npm install --quiet
cd ../..

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Start the backend:   cd src/backend && uvicorn app.main:app --reload"
echo "Start the frontend:  cd src/frontend && npm run dev"
echo "View API docs:       http://localhost:8000/api/v1/docs"
echo "View frontend:       http://localhost:3000"
echo "Redpanda console:    http://localhost:8080"
echo "MinIO console:       http://localhost:9001"
