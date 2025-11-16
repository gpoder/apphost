# AppHost

A minimal multi-app dispatcher built with Flask, Blueprints, and
`DispatcherMiddleware`, using a flat-file storage adapter and designed to
live behind an NGINX reverse proxy.

## Features

- Flask with Blueprints
- DispatcherMiddleware to mount:
  - `/`      → root health + landing
  - `/admin` → admin UI for managing apps
  - `/apps`  → public-facing app endpoints
- Flat-file JSON storage adapter (easily extensible)
- NGINX reverse proxy configuration
- Zero-config install script for Ubuntu 24.04 (`install.sh`)
- Diagnostics script (`test_stack.sh`)

## Usage on Ubuntu 24.04

```bash
git clone <your-github-url>.git apphost
cd apphost
sudo ./install.sh
```

Then visit:

- http://<server-ip>/admin/
- http://<server-ip>/apps/
- http://<server-ip>/health

## Testing

```bash
./test_stack.sh
```

Diagnostics are written to `/tmp/apphost_diagnostics.txt`.
