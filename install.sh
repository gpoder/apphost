#!/usr/bin/env bash
set -e
set -o pipefail

echo "==============================================="
echo "  AppHost Zero-Config Installer"
echo "  Ubuntu 24.04 + NGINX (no default server)"
echo "==============================================="

if [[ "$EUID" -ne 0 ]]; then
    echo "❌ Please run as root: sudo ./install.sh"
    exit 1
fi

DISPATCHER_DIR="/opt/apphost"
APP_DIR="$DISPATCHER_DIR/app"
VENV_DIR="$APP_DIR/venv"
SYSTEMD_FILE="/etc/systemd/system/apphost.service"
NGINX_CONF="/etc/nginx/conf.d/apphost.conf"
DATA_DIR="/opt/apphost/data"

echo "🔧 Installing OS packages..."
apt update -y
apt install -y python3 python3-venv python3-pip nginx rsync

echo "📁 Creating directories..."
mkdir -p "$DISPATCHER_DIR" "$APP_DIR" "$DATA_DIR"

echo "📦 Syncing code into $APP_DIR ..."
rsync -a --delete --exclude 'venv' ./ "$APP_DIR/"

chown -R www-data:www-data "$DISPATCHER_DIR"
chmod -R 755 "$DISPATCHER_DIR"

echo "🐍 Setting up Python virtualenv..."
if [[ ! -d "$VENV_DIR" ]]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
deactivate

echo "📝 Writing systemd service to $SYSTEMD_FILE ..."
cat > "$SYSTEMD_FILE" <<EOF
[Unit]
Description=AppHost Dispatcher (Gunicorn)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="APPHOST_DATA_DIR=$DATA_DIR"
ExecStart=$VENV_DIR/bin/gunicorn --workers 3 --bind unix:$DISPATCHER_DIR/apphost.sock apphost:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Reloading systemd..."
systemctl daemon-reload
systemctl enable apphost
systemctl restart apphost || true

echo "🛑 Disabling default NGINX site (if present)..."
DEFAULT_AVAIL="/etc/nginx/sites-available/default"
DEFAULT_ENABLED="/etc/nginx/sites-enabled/default"

if [[ -L "$DEFAULT_ENABLED" || -f "$DEFAULT_ENABLED" ]]; then
    rm -f "$DEFAULT_ENABLED"
    echo "✔ Removed /etc/nginx/sites-enabled/default"
fi

if [[ -f "$DEFAULT_AVAIL" ]]; then
    mv "$DEFAULT_AVAIL" "$DEFAULT_AVAIL.disabled" 2>/dev/null || true
    echo "✔ Renamed /etc/nginx/sites-available/default to .disabled"
fi

echo "🌐 Writing NGINX config to $NGINX_CONF ..."
if [[ -f "$NGINX_CONF" ]]; then
    cp "$NGINX_CONF" "$NGINX_CONF.bak-$(date +%s)"
fi

cat > "$NGINX_CONF" <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name _;

    access_log /var/log/nginx/apphost_access.log;
    error_log  /var/log/nginx/apphost_error.log;

    # Health check
    location = /health {
        proxy_pass http://unix:$DISPATCHER_DIR/apphost.sock:;
        proxy_set_header Host \$host;
    }

    # Avoid favicon spam
    location = /favicon.ico {
        empty_gif;
    }

    # Static assets (shared between admin/apps UIs)
    location /static/ {
        alias $APP_DIR/apphost/static/;
    }

    # Admin UI
    location /admin/ {
        proxy_pass http://unix:$DISPATCHER_DIR/apphost.sock:/admin/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Apps UI
    location /apps/ {
        proxy_pass http://unix:$DISPATCHER_DIR/apphost.sock:/apps/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Root landing page
    location / {
        proxy_pass http://unix:$DISPATCHER_DIR/apphost.sock:;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo "🔍 Testing NGINX configuration..."
nginx -t

echo "🔄 Restarting NGINX..."
systemctl restart nginx

echo "==============================================="
echo " ✅ AppHost install/update complete"
echo "==============================================="
echo "Admin UI:  http://<server-ip>/admin/"
echo "Apps:      http://<server-ip>/apps/"
echo "Health:    http://<server-ip>/health"
echo "==============================================="
