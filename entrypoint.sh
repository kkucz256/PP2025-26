#!/bin/sh
set -e

# Install Python dependencies at container start (allows updating requirements without rebuilding image)
if [ -f /app/requirements.txt ]; then
  echo "Installing Python dependencies from /app/requirements.txt..."
  pip install --no-cache-dir -r /app/requirements.txt || echo "pip install failed"
fi

# Optionally run migrations if MIGRATE=true
if [ "${MIGRATE}" = "true" ]; then
  echo "Running Django migrations..."
  python manage.py makemigrations --noinput || true
  python manage.py migrate --noinput || true
fi

# Execute the container CMD
exec "$@"
