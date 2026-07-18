from flask import Blueprint, render_template, session

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/about", endpoint="about")
def about():
    return render_template("about_us.html")


@pages_bp.route("/support", endpoint="support")
def support():
    return render_template("support.html")


@pages_bp.route("/profile", endpoint="profile")
def profile():
    return render_template("profile.html", username=session.get("username", "").removesuffix("@gmail.com"))
