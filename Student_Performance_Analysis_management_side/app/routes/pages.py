from flask import Blueprint, render_template, session, request, redirect, url_for, current_app

from app.extensions import db
from app.models import Teacher

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/about", endpoint="about")
def about():
    return render_template("about_us.html")


@pages_bp.route("/support", endpoint="support")
def support():
    return render_template("support.html")


@pages_bp.route("/forget_pass", methods=["GET", "POST"], endpoint="forgot_password")
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not email or not new_password or not confirm_password:
            return render_template("forgot_password.html", error="Please fill in all fields.")

        if new_password != confirm_password:
            return render_template("forgot_password.html", error="Passwords do not match.")

        teacher = Teacher.query.filter(Teacher.Gmail == email).first()
        if not teacher:
            return render_template("forgot_password.html", error="No teacher account found for that email.")

        teacher.password = new_password
        db.session.commit()
        current_app.logger.info(f"Password reset requested for {email}")
        return render_template("success.html", data="Password updated successfully!", location="/")

    return render_template("forgot_password.html")


@pages_bp.route("/profile", endpoint="profile")
def profile():
    return render_template("profile.html", username=session.get("username", "").removesuffix("@gmail.com"))

@pages_bp.route("/register",endpoint="register")
def register():
    return render_template("register.html")