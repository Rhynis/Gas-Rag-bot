#!/bin/bash
set -e

ENVIRONMENT="${ENVIRONMENT:-development}"

if [ "$ENVIRONMENT" = "production" ]; then
  echo "You are about to run production database migrations."
  read -r -p "Type 'migrate production' to continue: " CONFIRMATION
  if [ "$CONFIRMATION" != "migrate production" ]; then
    echo "Migration cancelled."
    exit 1
  fi
fi

(cd backend && alembic upgrade head)
