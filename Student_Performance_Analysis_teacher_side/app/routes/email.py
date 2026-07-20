from flask import Blueprint, render_template, request, session, jsonify, current_app

from config import dict_details
from app.models import Student, Exam, Mark
from app.services.email_service import email
from app.utils.Logged_in import login_required

email_bp = Blueprint("email", __name__)


@email_bp.route("/loading", endpoint="loading")
def loading():
    """Shown immediately after the user clicks 'Send Results'.
    This page's JS fires the actual /send_results request in the background
    and then redirects to /success or /error_page once it finishes."""
    sub = request.args.get("sub", "")
    exa = request.args.get("exam", "")
    return render_template("loading.html", sub=sub, exam=exa)


@email_bp.route("/success", endpoint="success")
def success():
    sent_count = request.args.get("sent", "0")
    sub = request.args.get("sub", "")
    exa = request.args.get("exam", "")
    current_app.logger.info(f"{session.get('username', '')} susccesfully sent emails")
    return render_template("success.html", sent_count=sent_count, sub=sub, exam=exa)


@email_bp.route("/error_page", endpoint="error_page")
def error_page():
    msg = request.args.get("msg", "Something went wrong while sending results.")
    current_app.logger.error("Something went wrong while sending results.")
    return render_template("Error.html", data=msg, location="/home")


@email_bp.route("/send_results", methods=["POST"], endpoint="send_results")
@login_required
def send_results():
    """Called via fetch() from loading.html. Returns JSON, not HTML,
    so the loading page's JS can decide where to redirect next."""
    PASSWORD = dict_details.get(session.get("username", ""))
    if not PASSWORD:
        return jsonify({"status": "error", "message": "Could not find email credentials for this account."}), 400

    class_value = session.get("class_value")
    sec = session.get("sec")
    sub = request.form.get("subject10", "") or request.form.get("subject12", "")
    exa = request.form.get("exam", "")

    if not sub or not exa or class_value is None:
        return jsonify({"status": "error", "message": "Missing subject, exam, or class information."}), 400

    students = Student.query.filter(
        Student.student_class == class_value,
        Student.section == sec
    ).all()

    exam = Exam.query.filter(Exam.exam_name == exa).first()
    res = []
    if exam is not None:
        res = Mark.query.filter(
            Mark.student_class == class_value,
            Mark.exam_id == exam.exam_id,
            Mark.subject == sub
        ).all()

    sent_count = 0
    for stu in students:
        for mark in res:
            if stu.roll_no == mark.roll_no:
                status = "passed" if mark.marks > 30 else "failed"
                msg = f"""Dear Parent/Guardian,

This is to inform you that {stu.student_name} has scored {mark.marks} marks and {status} in {sub} for the {exa}.
We encourage you to review the student's progress and continue supporting their learning.
Thank you for your cooperation.

Regards,
School Administration"""
                try:
                    email(session.get("username", ""), stu.student_gmail, f"{sub}-{exa}-Marks", msg, PASSWORD)
                    sent_count += 1
                except Exception as e:
                    current_app.logger.error(e)
                    return jsonify({"status": "error", "message": f"{e}\nContact the developer"}), 500

    return jsonify({"status": "success", "sent_count": sent_count})
