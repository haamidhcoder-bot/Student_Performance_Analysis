from flask import Blueprint, render_template, redirect, request, session, current_app
from sqlalchemy import func

from app.extensions import db
from app.models import Student, Exam, Mark

home_bp = Blueprint("home", __name__)


@home_bp.route("/home", endpoint="home", strict_slashes=False)
def home():
    return render_template(
        "Home.html",
        class_value=session.get("class_value", ""),
        sub="",
        sec=session.get("sec", "")
    )


@home_bp.route("/refresh", methods=["GET", "POST"], endpoint="refresh")
def refresh():
    if request.method == "POST":
        class_input = request.form.get("class", "").strip()
        if class_input:
            try:
                class_input = int(class_input)
            except ValueError:
                return render_template(
                    "Home.html",
                    class_value=session.get("class_value", ""),
                    sub="",
                    sec=session.get("sec", ""),
                    error="Invalid class value."
                )
            students_exist = Student.query.filter(Student.student_class == class_input).first()
            if not students_exist:
                current_app.logger.error("No matching students found")
                return render_template(
                    "Home.html",
                    class_value=session.get("class_value", ""),
                    sub="",
                    sec=session.get("sec", ""),
                    error="No matching students found."
                )
            session["class_value"] = class_input

        class_value = session.get("class_value")
        if class_value is None:
            return render_template(
                "Home.html",
                class_value="",
                sub="",
                sec=session.get("sec", ""),
                error="Please select a class first."
            )

        sec = request.form.get("section", "").strip() or session.get("sec", "")
        session["sec"] = sec
        sub = request.form.get("subject10", "") or request.form.get("subject12", "")
        exa = request.form.get("exam10", "") or request.form.get("exam12", "")
        students = Student.query.filter(
            Student.student_class == class_value,
            Student.section == sec
        ).all()

        exam = Exam.query.filter(Exam.exam_name == exa).first() if exa else None
        res = []
        if exam is not None and sub and exa:
            res = Mark.query.filter(
                Mark.student_class == class_value,
                Mark.exam_id == exam.exam_id,
                Mark.subject == sub
            ).all()

        if sub == "All" and exam is not None:
            totals = db.session.query(
                Mark.roll_no,
                func.sum(Mark.marks).label("total")
            ).filter(
                Mark.student_class == class_value,
                Mark.exam_id == exam.exam_id
            ).group_by(Mark.roll_no).all()

            total_marks = {row.roll_no: row.total for row in totals}
            return render_template(
                "Home.html",
                class_value=class_value,
                students=students,
                total_marks=total_marks,
                sub=sub,
                exam=exa,
                sec=sec
            )

        if sub and exa:
            return render_template(
                "Home.html",
                class_value=class_value,
                students=students,
                results=res,
                sub=sub,
                exam=exa,
                sec=sec
            )

        # Class was (re)selected but no subject/exam picked yet - show the
        # empty state instead of erroring, since class selection now shares
        # this same form.
        return render_template(
            "Home.html",
            class_value=class_value,
            sub="",
            sec=sec
        )

    return redirect("/home")
