"""Performance-graph generation, extracted from the original `/graph` route.

The matplotlib/seaborn plotting logic and all queries are identical to the
original code (including the `res` and `students` queries, which were
computed but not actually used in the plot in the original version - kept
as-is since the request was to reorganize, not to change behavior).
"""
from io import BytesIO
import base64

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from app.models import Exam, Mark, Student


def generate_graph(roll_no, subject, exam_id, class_value, sec):
    exam_all = Exam.query.order_by(Exam.exam_id).all()

    res = Mark.query.filter(
        Mark.student_class == class_value,
        Mark.exam_id == exam_id,
        Mark.subject == subject
    ).all()

    students = Student.query.filter(
        Student.student_class == class_value,
        Student.section == sec
    ).all()

    mark = Mark.query.filter(
        Mark.roll_no == roll_no,
        Mark.subject == subject
    ).all()

    exam = Exam.query.filter(Exam.exam_id == exam_id).first()
    exam1 = exam.exam_name

    # Seaborn Theme
    sns.set_theme(style="white")

    # Create Figure
    fig, ax = plt.subplots(figsize=(12, 6))

    # Background Color
    bg = "#1565A6"          # Light Blue
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    # Grid
    ax.grid(
        True,
        color="white",
        linewidth=0.8,
        alpha=0.35
    )

    ax.minorticks_on()

    ax.grid(
        which="minor",
        color="white",
        linewidth=0.4,
        alpha=0.25
    )

    df = pd.DataFrame({"Exam": [exa.exam_name for exa in exam_all], "Marks": [m.marks for m in mark]})

    # Line Plot (Seaborn)
    sns.lineplot(
        data=df,
        x="Exam",
        y="Marks",
        color="white",
        linewidth=3,
        marker="o",
        markersize=9,
        ax=ax
    )

    # Fill Area
    ax.fill_between(
        df["Exam"],
        df["Marks"],
        color="white",
        alpha=0.18
    )

    # Axis Styling
    ax.tick_params(colors="white", labelsize=12)

    for spine in ax.spines.values():
        spine.set_color("white")
        spine.set_alpha(0.5)

    # Labels
    plt.title(
        f"Student Performance {roll_no}",
        fontsize=22,
        color="white",
        weight="bold",
        pad=20
    )

    plt.xlabel(
        f"Exam {exam1}",
        fontsize=14,
        color="white"
    )

    plt.ylabel(
        f"{subject} Marks",
        fontsize=14,
        color="white"
    )

    # Value Labels
    for x, y in zip(df["Exam"], df["Marks"]):
        plt.text(
            x,
            y + 2,
            str(y),
            color="white",
            fontsize=11,
            ha="center"
        )

    plt.ylim(0, 100)

    sns.despine(left=False, bottom=False)

    plt.tight_layout()
    buffer = BytesIO()

    plt.savefig(buffer, format="png")

    buffer.seek(0)

    graph_base64 = base64.b64encode(buffer.getvalue()).decode()

    plt.close()

    return graph_base64, exam1
