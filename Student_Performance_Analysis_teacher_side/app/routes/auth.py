from flask import Blueprint, render_template, redirect, request, session, url_for, current_app

from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Teacher

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/", methods=["POST", "GET"], endpoint="login_page")
def login_page():
    if request.method == "POST" and not session.get("logged_in", ""):
        user_n = request.form.get("username", "")
        pass_n =request.form.get("password", "")
        session["username"] = user_n
        remember = request.form.get("remember", "")
        teachers = Teacher.query.filter(
            Teacher.Gmail == user_n
        ).first()
        if remember and teachers:
            session["logged_in"] = True
        if teachers and check_password_hash(teachers.password,pass_n):#for working of password hashing the password saved in database should be in the same hashing
            current_app.logger.info(f"{session.get('username', '')} logged in")
            return render_template(
                "Home.html",
                class_value=int(session.get("class_value", 0)),
                sub="",
                sec=session.get("sec", "")
            )
        else:
            current_app.logger.error("incorrect username or password")
            return render_template("Error.html", data=" incorrect username or password", location="/")
    elif session.get("logged_in", ""):
        current_app.logger.info(f"{session.get('username', '')} logged in back")
        return render_template(
            "Home.html",
            class_value=int(session.get("class_value", 0)),
            sub="",
            sec=session.get("sec", ""),
            log=session.get("logged_in", ""),
            user=session.get("username", "")
        )
    return render_template("login_page.html")


@auth_bp.route("/log-out", methods=["POST", "GET"])
def log_out():
    current_app.logger.info(f"{session.get('username', '')} has logged out")
    session.clear()
    session["logged_in"] = False
    return redirect(url_for("auth.login_page"))
