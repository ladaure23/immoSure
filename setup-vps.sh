#!/usr/bin/env bash
# ImmoSure VPS Setup — Ubuntu 22.04
# Usage: sudo bash setup-vps.sh

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/yourorg/immosure.git}"
APP_DIR="/var/www/immosure"
LOG_DIR="/var/log/immosure"
UPLOAD_DIR="/uploads/receipts"
DB_NAME="immosure"
DB_USER="immosure"
DB_PASS="${DB_PASSWORD:-$(openssl rand -hex 16)}"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# ─── System packages ──────────────────────────────────────────
log "Updating system packages..."
apt-get update -y && apt-get upgrade -y
apt-get install -y \
    curl wget gnupg2 ca-certificates lsb-release \
    build-essential libssl-dev libffi-dev libpq-dev \
    git unzip software-properties-common \
    libpango-1.0-0 libpangoft2-1.0-0 libgdk-pixbuf2.0-0 \
    libcairo2 libgirepository1.0-dev gir1.2-pango-1.0

# ─── Python 3.11 ──────────────────────────────────────────────
log "Installing Python 3.11..."
add-apt-repository ppa:deadsnakes/ppa -y
apt-get update -y
apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
python3 --version

# ─── PostgreSQL 15 ────────────────────────────────────────────
log "Installing PostgreSQL 15..."
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
    | gpg --dearmor -o /usr/share/keyrings/postgresql.gpg
echo "deb [signed-by=/usr/share/keyrings/postgresql.gpg] \
    https://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" \
    > /etc/apt/sources.list.d/pgdg.list
apt-get update -y
apt-get install -y postgresql-15 postgresql-client-15

systemctl enable postgresql
systemctl start postgresql

log "Creating database and user..."
sudo -u postgres psql <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';
  END IF;
END
\$\$;
CREATE DATABASE IF NOT EXISTS ${DB_NAME} OWNER ${DB_USER};
GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
SQL

log "PostgreSQL DB '${DB_NAME}' ready. Password: ${DB_PASS}"

# ─── Node.js 20 ───────────────────────────────────────────────
log "Installing Node.js 20..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
node --version && npm --version

# ─── PM2 ──────────────────────────────────────────────────────
log "Installing PM2..."
npm install -g pm2
pm2 --version

# ─── nginx ────────────────────────────────────────────────────
log "Installing nginx..."
apt-get install -y nginx
systemctl enable nginx
systemctl start nginx

# ─── Directories ──────────────────────────────────────────────
log "Creating application directories..."
mkdir -p "${LOG_DIR}" "${UPLOAD_DIR}" "${APP_DIR}"
chown -R www-data:www-data "${UPLOAD_DIR}"
chmod -R 755 "${UPLOAD_DIR}"

# ─── Clone repository ─────────────────────────────────────────
log "Cloning repository..."
if [ -d "${APP_DIR}/.git" ]; then
    git -C "${APP_DIR}" pull
else
    git clone "${REPO_URL}" "${APP_DIR}"
fi

# ─── Python venv + dependencies ───────────────────────────────
log "Setting up Python virtual environment..."
python3.11 -m venv "${APP_DIR}/venv"
"${APP_DIR}/venv/bin/pip" install --upgrade pip wheel
"${APP_DIR}/venv/bin/pip" install -r "${APP_DIR}/backend/requirements.txt"

# ─── Environment file ─────────────────────────────────────────
if [ ! -f "${APP_DIR}/backend/.env" ]; then
    log "Copying .env.example → .env (edit before starting)"
    cp "${APP_DIR}/backend/.env.example" "${APP_DIR}/backend/.env"
    sed -i "s|postgresql+asyncpg://immosure:password@|postgresql+asyncpg://${DB_USER}:${DB_PASS}@|" \
        "${APP_DIR}/backend/.env"
fi

# ─── Alembic migrations ───────────────────────────────────────
log "Running database migrations..."
cd "${APP_DIR}/backend"
"${APP_DIR}/venv/bin/alembic" upgrade head

# ─── Frontend build ───────────────────────────────────────────
log "Building frontend..."
cd "${APP_DIR}/frontend"
npm ci
npm run build

# ─── nginx config ─────────────────────────────────────────────
log "Configuring nginx..."
cp "${APP_DIR}/nginx.conf" /etc/nginx/sites-available/immosure
ln -sf /etc/nginx/sites-available/immosure /etc/nginx/sites-enabled/immosure
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# ─── PM2 startup ──────────────────────────────────────────────
log "Starting PM2 processes..."
cd "${APP_DIR}"
pm2 start ecosystem.config.js
pm2 save

# PM2 autostart on reboot
env PATH="$PATH:/usr/bin" pm2 startup systemd -u root --hp /root

log "=========================================================="
log "ImmoSure setup complete!"
log "DB password saved: ${DB_PASS}"
log "Edit ${APP_DIR}/backend/.env before starting services."
log "=========================================================="
