import os
from flask import Flask, render_template, abort, request, Response
import requests
from .models.app_registry import list_apps, get_app
from .container_engine import ensure_container_running

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

def _proxy_container(app_data, slug, subpath):
    """Reverse proxy HTTP to the container for this app."""
    host_port = ensure_container_running(app_data)
    # Build upstream URL
    # We strip /apps/<slug>/ prefix and send remaining path to container
    path = subpath or ""
    if path and not path.startswith("/"):
        path = "/" + path
    upstream = f"http://127.0.0.1:{host_port}{path}"

    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

    try:
        resp = requests.request(
            method=request.method,
            url=upstream,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True,
        )
    except requests.RequestException as e:
        return Response(f"Upstream error: {e}", status=502)

    excluded = {"content-encoding", "content-length", "transfer-encoding", "connection"}
    response_headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded]

    return Response(resp.content, status=resp.status_code, headers=response_headers)

def create_apps_app():
    app = Flask("apps_app", template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

    @app.route("/")
    def apps_index():
        apps = list_apps()
        return render_template("apps/index.html", apps=apps)

    @app.route("/<slug>/", defaults={"subpath": ""})
    @app.route("/<slug>/<path:subpath>")
    def app_view(slug, subpath):
        app_data = get_app(slug)
        if not app_data:
            abort(404)

        if app_data.get("type") == "container":
            return _proxy_container(app_data, slug, subpath)
        else:
            # Native app: simple detail page for now
            return render_template("apps/app_view.html", app_data=app_data)

    return app
