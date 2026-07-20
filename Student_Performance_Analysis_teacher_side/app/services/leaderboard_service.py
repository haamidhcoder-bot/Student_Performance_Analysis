"""Leaderboard computation, extracted from the original `/leaderboard` route.

Only the query/aggregation part was pulled out (form parsing, session
handling, and rendering stay in app/routes/reports.py). The SQL and the
podium/total_marks calculation are identical to the original code.
"""
from sqlalchemy import func

from app.extensions import db
from app.models import Student, Exam, Mark


def compute_leaderboard(class_value, exam_name):
    """Returns (students, podium, total_marks) for the given class/exam,
    or None if the exam does not exist (caller keeps the original
    'render leaderboard.html with just class_value' fallback in that case).
    """
    students = Student.query.filter(
        Student.student_class == class_value
    ).all()

    exam = Exam.query.filter(Exam.exam_name == exam_name).first()
    if exam is None:
        return None

    leaderboard = db.session.query(
        Mark.roll_no,
        func.sum(Mark.marks).label("total")
    ).filter(
        Mark.student_class == class_value,
        Mark.exam_id == exam.exam_id
    ).group_by(Mark.roll_no).order_by((func.sum(Mark.marks)).desc()).all()

    name_lookup = {stu.roll_no: stu.student_name for stu in students}
    podium = [
        {
            "rank": idx,
            "name": name_lookup.get(roll_no, "Unknown"),
            "marks": total
        }
        for idx, (roll_no, total) in enumerate(leaderboard[:3], start=1)
    ]

    total_marks = {row.roll_no: row.total for row in leaderboard[3:]}

    return students, podium, total_marks
