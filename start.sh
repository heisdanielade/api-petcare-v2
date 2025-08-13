#!/bin/bash
set -e

echo "(i) Checking if Alembic is in sync..."

# If the alembic_version table does not exist, stamp to head before running migrations
if ! psql "$DATABASE_URL" -tAc "SELECT 1 FROM alembic_version LIMIT 1;" >/dev/null 2>&1; then
    echo "(i) No alembic_version table found — stamping to head."
    alembic stamp head
fi


echo "(i) Running Alembic migrations..."
alembic downgrade -1
alembic upgrade head || { echo "(e) Alembic upgrade failed"; exit 1; }

echo "(i) Showing migration history..."
alembic history
alembic current

echo "(i) Starting FastAPI app with Gunicorn..."
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 3

