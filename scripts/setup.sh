#!/bin/bash
set -e

echo "==========================================="
echo "GasBot Vietnam - Development Setup"
echo "==========================================="

command -v docker >/dev/null 2>&1 || { echo "Docker required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js required but not installed."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python 3 required but not installed."; exit 1; }

NODE_VERSION=$(node -v | cut -d 'v' -f 2 | cut -d '.' -f 1)
if [ "$NODE_VERSION" -lt 20 ]; then
  echo "Node.js 20+ required (found $NODE_VERSION)"
  exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [ "$(printf '%s\n' "3.11" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.11" ]; then
  echo "Python 3.11+ required (found $PYTHON_VERSION)"
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example - please configure"
fi

echo "Starting Docker services..."
docker compose up -d

echo "Waiting for PostgreSQL..."
until docker compose exec -T postgres pg_isready -U gasbot > /dev/null 2>&1; do
  sleep 1
done

echo "Waiting for Redis..."
until docker compose exec -T redis redis-cli ping > /dev/null 2>&1; do
  sleep 1
done

echo "==========================================="
echo "Setup complete! Next steps:"
echo "1. cd backend && python -m venv venv && source venv/bin/activate"
echo "2. pip install -r requirements.txt -r requirements-dev.txt"
echo "3. alembic upgrade head"
echo "4. cd ../frontend && npm install"
echo "5. make dev"
echo "==========================================="
