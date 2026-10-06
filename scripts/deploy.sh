#!/usr/bin/env bash
# ==============================================================================
# Deployment script for General Development System (GDS)
# ==============================================================================
set -euo pipefail

APP_DIR="/opt/gds"
REPO_URL="https://github.com/abdalazeim/GDS.git"
BRANCH="main"
ENV_FILE="${APP_DIR}/.env"
VENV_DIR="${APP_DIR}/venv"
SERVICE_NAME="gds"

echo "=== Deploying General Development System (GDS) ==="

# 1. Pull latest code
cd "${APP_DIR}"
git fetch origin
git checkout "${BRANCH}"
git pull origin "${BRANCH}"

# 2. Activate virtual environment
source "${VENV_DIR}/bin/activate"

# 3. Install / update dependencies
pip install --upgrade pip
pip install -r requirements.txt --no-deps

# 4. Apply database migrations
python manage.py migrate --noinput --settings=config.settings.production

# 5. Collect static files
python manage.py collectstatic --noinput --clear --settings=config.settings.production

# 6. Restart application
echo "Restarting ${SERVICE_NAME}..."
if systemctl is-active --quiet "${SERVICE_NAME}"; then
    sudo systemctl restart "${SERVICE_NAME}"
else
    sudo systemctl start "${SERVICE_NAME}"
fi

echo "=== Deployment complete ==="
