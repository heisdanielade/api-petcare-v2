#!/bin/bash
set -e

echo "(i) Checking if Alembic is in sync..."

# Check if alembic_version table exists
if ! psql "$DATABASE_URL" -tAc "SELECT 1 FROM information_schema.tables WHERE table_name='alembic_version';" | grep -q 1; then
    echo "(e) ERROR: No alembic_version table found."
    echo "    This database has never been migrated."
    echo "    Please run migrations manually before starting the app."
    exit 1
fi


echo "(i) Running Alembic migrations..."
alembic upgrade head || { echo "(e) Alembic upgrade failed"; exit 1; }


# List of columns to verify
REQUIRED_COLUMNS=(
    "users.is_deleted"
    "users.updated_at"
    "users.created_at"
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

