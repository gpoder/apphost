import os
from flask import Flask, render_template, abort
from .models.app_registry import list_apps, get_app

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

def create_apps_app():
    app = Flask("apps_app", template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

    @app.route("/")
    def apps_index():
        apps = list_apps()
        return render_template("apps/index.html", apps=apps)

    @app.route("/<slug>/")
    def app_view(slug):
        app_data = get_app(slug)
        if not app_data:
            abort(404)
        return render_template("apps/app_view.html", app_data=app_data)

    return app
