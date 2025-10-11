#!/bin/bash
set -e

echo "(i) Checking for PostgreSQL client (psql)..."
if ! command -v psql >/dev/null 2>&1; then
    echo "(e) psql command not found. Please install PostgreSQL client."
    exit 1
fi

echo "(i) Checking if Alembic is in sync..."
# If alembic_version table does not exist, stamp to head before running migrations
if ! psql "$DATABASE_URL" -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version';" | grep -q 1; then
    echo "(i) No alembic_version table found — stamping to head."
    alembic stamp head
fi

echo "(i) Running Alembic migrations..."
alembic upgrade head || { echo "(e) Alembic upgrade failed"; exit 1; }

# List of columns to verify
REQUIRED_COLUMNS=(
    "app_user.is_deleted"
    "app_user.updated_at"
    "app_user.created_at"
)

for col in "${REQUIRED_COLUMNS[@]}"; do
    TABLE="${col%%.*}"
    COLUMN="${col##*.}"
    EXISTS=$(psql "$DATABASE_URL" -tAc "
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = '$TABLE' AND column_name = '$COLUMN';
    ")
    if [ "$EXISTS" != "1" ]; then
        echo "(e) Schema verification failed: '$COLUMN' column missing from '$TABLE' table."
        exit 1
    fi
done

echo "(i) Showing migration history..."
alembic history
alembic current

echo "(i) Starting FastAPI app with Gunicorn..."
gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 3
