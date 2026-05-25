#!/bin/bash
set -e

echo "Running backend tests..."
if [ -f backend/requirements.txt ]; then
  (cd backend && pytest --cov=app --cov-report=term-missing)
else
  echo "Skipping backend tests: backend/requirements.txt not found"
fi

echo "Running frontend tests..."
if [ -f frontend/package.json ]; then
  (cd frontend && npm test -- --run)
else
  echo "Skipping frontend tests: frontend/package.json not found"
fi
