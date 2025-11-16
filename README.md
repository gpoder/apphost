# AppHost (Container-enabled)

AppHost is a minimal multi-app dispatcher built on Flask + DispatcherMiddleware,
designed to live behind NGINX and now capable of running **containerized apps**
(WSGI, ASGI, Node, anything HTTP) alongside native views.

## Features

- Flask + Blueprints
- `DispatcherMiddleware` mounts:
  - `/`      → root landing + health check
  - `/admin` → admin UI for managing apps
  - `/apps`  → public apps index + per-app endpoints
- Flat-file JSON storage adapter (`FlatFileStorage`)
- NGINX reverse proxy front-end
- Zero-config install script for Ubuntu 24.04 (`install.sh`)
- Diagnostics script (`test_stack.sh`)
- **Container app support**:
  - Mode `pull`: run arbitrary images (FastAPI, Node, etc.)
  - Mode `build`: build from Docker context + Dockerfile
  - Automatic HTTP proxying via Python to `127.0.0.1:<host_port>`

## Local development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export APPHOST_DATA_DIR=$(pwd)/data
mkdir -p "$APPHOST_DATA_DIR"
python -m apphost
```

Open:

- http://127.0.0.1:5000/
- http://127.0.0.1:5000/admin/
- http://127.0.0.1:5000/apps/

## Deployment on Ubuntu 24.04

```bash
git clone https://github.com/<your-user>/<your-repo>.git apphost
cd apphost
sudo ./install.sh
```

The installer will:

- Install Python, NGINX, Docker
- Copy code to `/opt/apphost/app`
- Create `/opt/apphost/data` for flat-file storage
- Create a venv + install requirements
- Create + start `apphost.service` (Gunicorn via unix socket)
- Disable the default NGINX site
- Install `/etc/nginx/conf.d/apphost.conf` and restart NGINX

After that:

- Admin UI:  `http://<server-ip>/admin/`
- Apps:      `http://<server-ip>/apps/`
- Health:    `http://<server-ip>/health`

## Container apps

In the Admin UI:

1. Click **Create New App**
2. Set `Type = Container`
3. Fill in:
   - **Mode**:
     - `Pull image` – use an existing image (`ghcr.io/...`, `docker.io/...`)
     - `Build from Dockerfile` – build from a context folder
   - **Image**:
     - For `pull`: any image name, e.g. `ghcr.io/user/my-fastapi:latest`
     - For `build`: tag to use, e.g. `apphost_myfastapi`
   - **Internal port**: port inside the container (e.g. 8000 for FastAPI)
   - **Host port**: port on `127.0.0.1` that AppHost will proxy to
   - **Build context**: path to Docker context (for `mode=build`)
   - **Data dir**: host directory to mount at `/data` in container
   - **Env**: newline-separated `KEY=VALUE` pairs

When a user hits:

```text
/apps/<slug>/...
```

AppHost will:

1. Load the app definition from storage
2. If `type == "container"`:
   - Call `ensure_container_running()` (build/pull + run container if needed)
   - Proxy the HTTP request to `http://127.0.0.1:<host_port>/...`
3. Return the upstream response back to the client.

This works for:

- Flask / Django (WSGI)
- FastAPI / Starlette (ASGI)
- Express / Koa / custom Node.js
- Any other HTTP service inside a container

## Diagnostics

```bash
./test_stack.sh
```

Writes:

- System info
- `systemctl status apphost`
- `nginx -t`
- `docker ps -a` for `apphost_*`
- `curl` for `/health`, `/admin/`, `/apps/`
- `/opt/apphost` directory tree

to `/tmp/apphost_diagnostics.txt`.
