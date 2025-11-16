
import os
from flask import Flask, render_template, abort
from .models.app_registry import list_apps, get_app

BASE=os.path.dirname(__file__)
TEMPL=os.path.join(BASE,"templates")
STAT=os.path.join(BASE,"static")

def create_apps_app():
    app=Flask("apps_app",template_folder=TEMPL,static_folder=STAT)

    @app.route("/")
    def index():
        return render_template("apps/index.html", apps=list_apps())

    @app.route("/<slug>/")
    def view(slug):
        item=get_app(slug)
        if not item: abort(404)
        return render_template("apps/app_view.html", app_data=item)

    return app
