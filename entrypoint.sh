#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting Wamato API on port 8002..."
exec gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8002 \
  --access-logfile - \
  --error-logfile -
