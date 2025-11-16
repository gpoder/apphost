from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Flask
from .admin_app import create_admin_app
from .apps_app import create_apps_app

def create_root_app():
    app = Flask("root")

    @app.route("/health")
    def health():
        return {"status": "ok"}

    @app.route("/")
    def index():
        return (
            "<h2>AppHost Installed</h2>"
            "<p>Admin UI: <a href='/admin/'>/admin/</a></p>"
            "<p>Apps: <a href='/apps/'>/apps/</a></p>"
        )

    return app

def create_dispatcher():
    root_app = create_root_app()
    admin_app = create_admin_app()
    apps_app = create_apps_app()

    return DispatcherMiddleware(
        root_app,
        {
            "/admin": admin_app,
            "/apps": apps_app,
        },
    )

# WSGI entrypoint
application = create_dispatcher()
