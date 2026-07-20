from flask import Blueprint, render_template, redirect, request, session, current_app

from app.extensions import db
from app.models import Mark
from app.utils.Logged_in import login_required

marks_bp = Blueprint("marks", __name__)


@marks_bp.route("/edit/<int:roll_no>/<string:subject>/<int:exam_id>", methods=["POST", "GET"], endpoint="edit")
@login_required
def edit(roll_no: int, subject: str, exam_id: int):
    mark = Mark.query.filter(
        Mark.roll_no == roll_no,
        Mark.subject == subject,
        Mark.exam_id == exam_id
    ).first()
    if request.method == "POST" and mark:
        mar = request.form["content"]  # to get info from input box
        mark.marks = mar
        try:
            current_app.logger.info(f"{session.get('username', '')} has editted marks of student with roll no {roll_no}")
            db.session.commit()  # commiting it
            return redirect("/home")  # back to home
        except Exception as e:
            current_app.logger.error(e)
            return redirect("/")
        # create a new task
    else:
        return render_template("edit.html", marks=mark)
