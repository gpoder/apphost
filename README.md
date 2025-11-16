# AppHost

AppHost is a minimal multi-app dispatcher built on Flask with Blueprints and
`DispatcherMiddleware`, designed to run behind NGINX with a flat-file JSON
storage backend.

## Features

- Flask + Blueprints
- `DispatcherMiddleware` to mount:
  - `/`      → root landing + health check
  - `/admin` → admin UI for managing apps
  - `/apps`  → public apps index + per-app pages
- Flat-file storage adapter (`FlatFileStorage`) with a pluggable interface
- NGINX reverse proxy configuration
- Zero-config install script for Ubuntu 24.04 (`install.sh`)
- Diagnostics script (`test_stack.sh`)

## Layout

- `apphost/` – Python package
  - `__init__.py` – WSGI dispatcher entrypoint (`application`)
  - `admin_app.py` – admin Flask app
  - `apps_app.py` – public apps Flask app
  - `storage/` – storage adapters (currently flat-file)
  - `models/` – registry helpers
  - `templates/` – Jinja2 templates (admin + apps)
  - `static/` – shared CSS

## Local development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export APPHOST_DATA_DIR=$(pwd)/data
mkdir -p "$APPHOST_DATA_DIR"
python -m apphost
```

Then open:

- http://127.0.0.1:5000/
- http://127.0.0.1:5000/admin/
- http://127.0.0.1:5000/apps/

## Deployment on Ubuntu 24.04

```bash
git clone https://github.com/<your-user>/<your-repo>.git apphost
cd apphost
sudo ./install.sh
```

This will:

- Install Python + NGINX
- Copy the code into `/opt/apphost/app`
- Create `/opt/apphost/data` for flat-file storage
- Create a virtualenv and install requirements
- Create and start `apphost.service` (Gunicorn behind a unix socket)
- Disable the NGINX default site
- Install `/etc/nginx/conf.d/apphost.conf` and restart NGINX

After installation:

- Admin UI:  `http://<server-ip>/admin/`
- Apps:      `http://<server-ip>/apps/`
- Health:    `http://<server-ip>/health`

## Diagnostics

```bash
./test_stack.sh
```

This script writes a full report to `/tmp/apphost_diagnostics.txt`, including:

- system info
- `systemctl status apphost`
- `nginx -t`
- `curl` results for `/health`, `/admin/`, `/apps/`
- directory listing of `/opt/apphost`

You can attach that file to bug reports or paste it into ChatGPT for help.
