#!/bin/bash
set -e

echo "(i) Running Alembic migrations..."
alembic upgrade head

echo "(i) Starting FastAPI app with Gunicorn..."
gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4

chmod +x start.sh
