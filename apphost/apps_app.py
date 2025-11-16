from flask import Flask, render_template, abort
from .models.app_registry import get_app, list_apps

def create_apps_app():
    app = Flask("apps_app", template_folder="templates", static_folder="static")

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
