#!/bin/sh
set -e

# Run database migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Execute passed command
exec "$@"
