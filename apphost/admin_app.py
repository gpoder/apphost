import os
from flask import Flask, render_template, request, redirect, url_for, flash
from .models.app_registry import list_apps, save_app, delete_app, get_app

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

def create_admin_app():
    app = Flask("admin_app", template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
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
            app_type = request.form.get("app_type", "native")

            app_data = {
                "slug": slug,
                "name": name,
                "description": description,
                "type": app_type,
            }

            if app_type == "container":
                container_mode = request.form.get("container_mode", "pull")
                image = request.form.get("container_image", "").strip()
                internal_port = request.form.get("container_internal_port", "").strip() or "8000"
                host_port = request.form.get("container_host_port", "").strip() or "0"
                env_text = request.form.get("container_env", "")
                build_context = request.form.get("container_build_context", ".")
                data_dir = request.form.get("container_data_dir", "")

                app_data["container"] = {
                    "mode": container_mode,
                    "image": image,
                    "internal_port": int(internal_port),
                    "host_port": int(host_port),
                    "env": env_text,
                    "build_context": build_context,
                    "data_dir": data_dir or None,
                }

            if not slug or not name:
                flash("Slug and Name are required.", "error")
            else:
                save_app(app_data)
                flash(f"App '{slug}' saved.", "success")
                return redirect(url_for("index"))

        return render_template("admin/new_app.html")

    @app.route("/apps/<slug>/edit", methods=["GET", "POST"])
    def edit_app(slug):
        app_data = get_app(slug)
        if not app_data:
            flash("App not found.", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()
            app_type = request.form.get("app_type", "native")

            app_data["name"] = name
            app_data["description"] = description
            app_data["type"] = app_type

            if app_type == "container":
                container = app_data.get("container", {}) or {}
                container_mode = request.form.get("container_mode", container.get("mode", "pull"))
                image = request.form.get("container_image", container.get("image", "")).strip()
                internal_port = request.form.get("container_internal_port", container.get("internal_port", 8000))
                host_port = request.form.get("container_host_port", container.get("host_port", 0))
                env_text = request.form.get("container_env", container.get("env", ""))
                build_context = request.form.get("container_build_context", container.get("build_context", "."))
                data_dir = request.form.get("container_data_dir", container.get("data_dir", ""))

                app_data["container"] = {
                    "mode": container_mode,
                    "image": image,
                    "internal_port": int(internal_port),
                    "host_port": int(host_port),
                    "env": env_text,
                    "build_context": build_context,
                    "data_dir": data_dir or None,
                }
            else:
                app_data["container"] = None

            save_app(app_data)
            flash("App updated.", "success")
            return redirect(url_for("index"))

        return render_template("admin/edit_app.html", app_data=app_data)

    @app.route("/apps/<slug>/delete", methods=["POST"])
    def delete_app_route(slug):
        delete_app(slug)
        flash("App deleted.", "success")
        return redirect(url_for("index"))

    return app
