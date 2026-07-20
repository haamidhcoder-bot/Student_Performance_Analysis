from flask import Blueprint, render_template, redirect, request, session, current_app
from sqlalchemy import func

from app.extensions import db
from app.models.student import Student

home_bp = Blueprint("home", __name__)


@home_bp.route("/home", endpoint="home", strict_slashes=False)
def home():
    class_value = int(session.get("class_value", 0)) or None
    sec = session.get("sec", "")


    if not class_value:
        return render_template("Home.html", class_value=None, sub="")

    students = Student.query.filter(
        Student.student_class == class_value,
        Student.section == sec
    ).all()
    return render_template(
            "Home.html",
            class_value=class_value,
            students=students
        )



@home_bp.route("/refresh", methods=["GET", "POST"], endpoint="refresh")
def refresh():
    if request.method == "POST":
        class_input = request.form.get("class", "").strip()
        if class_input:
            try:
                class_input = int(class_input)
            except ValueError:
                return render_template("Error.html",data="invalid class value", location="/home")
            students_exist = Student.query.filter(Student.student_class == class_input).first()
            if not students_exist:
                current_app.logger.error("No matching students found")
                return render_template("Error.html",data="No matching students found", location="/home")
            session["class_value"] = class_input

        class_value = session.get("class_value")
        if class_value is None:
                return render_template("Error.html",data="select a class first", location="/home")

        sec = request.form.get("section", "").strip() or session.get("sec", "")
        session["sec"] = sec
        sub = request.form.get("subject10", "") or request.form.get("subject12", "")
        exa = request.form.get("exam", "") 
        students = Student.query.filter(
            Student.student_class == class_value,
            Student.section == sec
        ).all()

        # Class was (re)selected but no subject/exam picked yet - show the
        # empty state instead of erroring, since class selection now shares
        # this same form.
        return render_template(
            "Home.html",
            class_value=class_value,
            sec=sec
        )

    return redirect("/home")

@home_bp.route("/show_students", methods=["GET", "POST"], endpoint="show_students")
def show_students():
    if request.method == "POST":
        class_input = request.form.get("class", "").strip()
        sec = request.form.get("section", "").strip() or session.get("sec", "")
        session["sec"] = sec
        if class_input:
            try:
                class_input = int(class_input)
            except ValueError:
                return render_template("Error.html",data="invalid class value", location="/home")
            students_exist = Student.query.filter(Student.student_class == class_input,Student.section==session.get("sec","")).all()
            if not students_exist:
                current_app.logger.error("No matching students found")
                return render_template("Error.html",data="No matching students found", location="/home")
            session["class_value"] = class_input

        class_value = session.get("class_value")
        if class_value is None:
                return render_template("Error.html",data="select a class first", location="/home")

        return render_template(
                "Home.html",
                class_value=class_value,
                sec=sec,
                students=students_exist
            )
    return redirect("/home")