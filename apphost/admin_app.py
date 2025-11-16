
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from .models.app_registry import list_apps, create_or_update_app, delete_app, get_app

BASE=os.path.dirname(__file__)
TEMPL=os.path.join(BASE,"templates")
STAT=os.path.join(BASE,"static")

def create_admin_app():
    app=Flask("admin_app",template_folder=TEMPL,static_folder=STAT)
    app.secret_key="apphost-secret"

    @app.route("/")
    def index():
        return render_template("admin/index.html", apps=list_apps())

    @app.route("/apps/new",methods=["GET","POST"])
    def new():
        if request.method=="POST":
            slug=request.form.get("slug","")
            name=request.form.get("name","")
            desc=request.form.get("description","")
            if not slug or not name:
                flash("Slug + Name required","error")
            else:
                create_or_update_app(slug,name,desc)
                flash("Created","success")
                return redirect(url_for("index"))
        return render_template("admin/new_app.html")

    @app.route("/apps/<slug>/edit",methods=["GET","POST"])
    def edit(slug):
        item=get_app(slug)
        if not item:
            flash("Not found","error")
            return redirect(url_for("index"))
        if request.method=="POST":
            name=request.form.get("name","")
            desc=request.form.get("description","")
            create_or_update_app(slug,name,desc)
            flash("Updated","success")
            return redirect(url_for("index"))
        return render_template("admin/edit_app.html", app_data=item)

    @app.route("/apps/<slug>/delete",methods=["POST"])
    def delete(slug):
        delete_app(slug)
        flash("Deleted","success")
        return redirect(url_for("index"))

    return app
