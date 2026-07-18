from flask import Blueprint, render_template, request, session

from app.models import Student
from app.services.graph_service import generate_graph
from app.services.leaderboard_service import compute_leaderboard

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/graph/<int:roll_no>/<string:subject>/<int:exam_id>", methods=["POST", "GET"], endpoint="graph")
def graph(roll_no: int, subject: str, exam_id: int):
    if subject:
        graph_image, _exam1 = generate_graph(
            roll_no=roll_no,
            subject=subject,
            exam_id=exam_id,
            class_value=session.get("class_value"),
            sec=session.get("sec")
        )
        return render_template("graph.html", graph=graph_image)


@reports_bp.route("/leaderboard", methods=["GET", "POST"], endpoint="leaderboard")
def leaderboard():
    exa = request.form.get("exam", "")
    class_input = request.form.get("class", "").strip()

    if class_input:
        try:
            class_input = int(class_input)
        except ValueError:
            return render_template(
                "leaderboard.html",
                class_value=session.get("class_value", ""),
                error="Invalid class value."
            )
        students_exist = Student.query.filter(Student.student_class == class_input).first()
        if not students_exist:
            return render_template(
                "leaderboard.html",
                class_value=session.get("class_value", ""),
                error="No matching students found."
            )
        session["class_value"] = class_input

    class_value = session.get("class_value")

    if exa and class_value is not None:
        result = compute_leaderboard(class_value, exa)
        if result is None:
            return render_template("leaderboard.html", class_value=class_value)

        students, podium, total_marks = result

        return render_template(
            "leaderboard.html",
            class_value=class_value,
            students=students,
            total_marks=total_marks,
            podium=podium,
            sub="All",
            exam=exa
        )
    return render_template("leaderboard.html", class_value=class_value if class_value is not None else "")
