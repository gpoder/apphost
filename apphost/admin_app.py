from flask import Flask, render_template, request, redirect, url_for, flash
from .models.app_registry import list_apps, create_or_update_app, delete_app, get_app

def create_admin_app():
    app = Flask("admin_app", template_folder="templates", static_folder="static")
    app.secret_key = "change-me-in-production"

    @app.route("/")
    def index():
        apps = list_apps()
        return render_template("admin/index.html", apps=apps)

    @app.route("/apps/new", methods=["GET", "POST"])
    def new_app():
        if request.method == "POST":
            slug = request.form.get("slug", "").strip()
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()
            if not slug or not name:
                flash("Slug and Name are required.", "error")
            else:
                create_or_update_app(slug, name, description)
                flash(f"App '{slug}' saved.", "success")
                return redirect(url_for("index"))
        return render_template("admin/new_app.html")

    @app.route("/apps/<slug>/edit", methods=["GET", "POST"])
    def edit_app(slug):
        app_data = get_app(slug)
        if not app_data:
            flash(f"App '{slug}' not found.", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()
            if not name:
                flash("Name is required.", "error")
            else:
                create_or_update_app(slug, name, description)
                flash(f"App '{slug}' updated.", "success")
                return redirect(url_for("index"))

        return render_template("admin/edit_app.html", app_data=app_data)

    @app.route("/apps/<slug>/delete", methods=["POST"])
    def delete_app_route(slug):
        delete_app(slug)
        flash(f"App '{slug}' deleted.", "success")
        return redirect(url_for("index"))

    return app
