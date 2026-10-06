#!/bin/bash
set -e

echo "================================================"
echo "  GDS Management System — Docker"
echo "================================================"

echo "[1/4] Waiting for database..."
python -c "
import time, os, psycopg2
from urllib.parse import urlparse
url = urlparse(os.environ.get('DATABASE_URL', ''))
host = url.hostname or 'db'
port = url.port or 5432
user = url.username or 'gds'
password = url.password or 'gds'
dbname = url.path.lstrip('/') or 'gds_dev'
for i in range(60):
    try:
        conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)
        conn.close()
        print('    ✅ Database ready after', i + 1, 'seconds')
        break
    except Exception:
        time.sleep(1)
else:
    print('    ❌ Database not ready after 60 seconds')
    exit(1)
"

echo "[2/4] Running migrations..."
python manage.py migrate --noinput
echo "    ✅ Migrations complete"

echo "[3/4] Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null || true
echo "    ✅ Static files collected"

echo "[4/4] Starting application..."
echo "================================================"
exec "$@"
