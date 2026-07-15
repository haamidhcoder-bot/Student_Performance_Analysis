#pip install -r requirements.txt
from flask import Flask,render_template,redirect,request,session,url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
import mysql.connector as sql
from sqlalchemy import func
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
import smtplib
from email.message import EmailMessage
from config import dict_details,Mysql_pass,session_key #contains password that are confidential
import logging
from logging.handlers import RotatingFileHandler
from io import BytesIO
import base64

cn = sql.connect(host='127.0.0.1', user='root', password=Mysql_pass)
cr = cn.cursor()
cr.execute("create database if not exists schooldb")


app=Flask(__name__)


app.secret_key = session_key  # required for sessions to work

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://root:{Mysql_pass}@localhost/schooldb"#format for using mysql
)

db = SQLAlchemy(app)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler = RotatingFileHandler(
    "app.log",
    maxBytes=1024 * 1024,  # 1 MB
    backupCount=5
)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

def email(from_address,to_address,subject,message,app_password):
    msg = EmailMessage()

    msg["Subject"] =subject
    msg["From"] = from_address
    msg["To"] = to_address

    msg.set_content(message)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()

        server.login(
            from_address,
            app_password
        )

        server.send_message(msg)

class Teacher(db.Model):
    __tablename__ = "teachers"

    Gmail = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(255), nullable=False)


class Student(db.Model):
    __tablename__ = "students"

    roll_no = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_class = db.Column("class", db.Integer, nullable=False)
    section = db.Column(db.String(1), nullable=False)
    student_gmail = db.Column(db.String(100))


class Exam(db.Model):
    __tablename__ = "exams"

    exam_id = db.Column(db.Integer, primary_key=True)
    exam_name = db.Column(db.String(50), unique=True, nullable=False)


class Mark(db.Model):
    __tablename__ = "marks"

    roll_no = db.Column(
        db.Integer,
        db.ForeignKey("students.roll_no"),
        primary_key=True
    )

    student_class= db.Column(
        "class", db.Integer,
        nullable=False
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("exams.exam_id"),
        primary_key=True
    )

    subject = db.Column(db.String(30), primary_key=True)

    marks = db.Column(db.Integer,default=0)

@app.route("/",methods=["post","get"])
def login_page():    
        if request.method=="POST":
            user_n=request.form.get("username","")
            pass_n=request.form.get("password","")
            """try:
                if session[user_n]:
                  pass_n=session[user_n]
            except:
                pass_n=request.form.get("password","")"""
            session["username"]=user_n
            session["password"]=pass_n
            remember=request.form.get("remember","")
            teachers=Teacher.query.filter(
                Teacher.Gmail==user_n,
                Teacher.password==pass_n
            ).first()
            """if remember:
                session[user_n]=pass_n"""
            if teachers:
                app.logger.info(f"{session.get("username","")} logged in")
                return render_template("class.html")
            else:
                app.logger.error("incorrect username or password")
                return render_template("Error.html",data=" incorrect username or password",location="/")
        return render_template("login_page.html")


@app.route("/data", methods=["GET", "POST"])
def data():
    if request.method == "POST":
        class_value = request.form.get("class", "").strip()
        sec = request.form.get("section", "").strip()

        if class_value:
            try:
                class_value = int(class_value)
            except:
                return render_template("class.html", error="Invalid class value.")
            session["class_value"] =class_value
            session["sec"]=sec
            students = Student.query.filter(
                Student.student_class == class_value,
                Student.section == sec
            ).all()
            if students:
                return render_template("Home.html", class_value=class_value,sub="")
        app.logger.error("No matching students found")
        return render_template("class.html", error="No matching students found.")

    return render_template("class.html")

@app.route("/home")
def home():
    return render_template("Home.html", class_value=session.get("class_value",""),sub="")

@app.route("/refresh", methods=["GET", "POST"])
def refresh():
    class_value = session.get("class_value")
    sec = session.get("sec")
    if request.method == "POST" and class_value is not None:
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
                exam=exa
            )

        if sub and exa:
            return render_template(
                "Home.html",
                class_value=class_value,
                students=students,
                results=res,
                sub=sub,
                exam=exa
            )
        elif sub=="" and exa=="":
            return render_template("Error.html",data="select the subject and exam",location="/data")
    
    return redirect("/data")

@app.route("/edit/<int:roll_no>/<string:subject>/<int:exam_id>", methods=["POST", "GET"])
def edit(roll_no:int, subject:str,exam_id:int):
    mark=Mark.query.filter(
        Mark.roll_no==roll_no,
        Mark.subject==subject,
        Mark.exam_id==exam_id
        ).first()
    if request.method=="POST" and mark:
        mar=request.form["content"]#to get info from input box 
        mark.marks=mar
        try:
            app.logger.info(f"{session.get("username","")} has editted marks of student with roll no {roll_no}")
            db.session.commit()#commiting it
            return redirect("/data")#back to home
        except Exception as e:
            app.logger.error(e)
            return redirect("/")
        #create a new task
    else:
        return render_template("edit.html",marks=mark)
    
@app.route("/graph/<int:roll_no>/<string:subject>/<int:exam_id>", methods=["POST", "GET"])
def graph(roll_no:int,subject:str,exam_id:int):
    if subject:
        exam_all=Exam.query.order_by(Exam.exam_id).all()
        res = Mark.query.filter(
                Mark.student_class == session.get("class_value"),
                Mark.exam_id == exam_id,
                Mark.subject == subject
            ).all()
                    
        students = Student.query.filter(
            Student.student_class == session.get("class_value"),
            Student.section == session.get("sec")
        ).all()

        mark=Mark.query.filter(
                Mark.roll_no==roll_no,
                Mark.subject==subject
                ).all()
        
        exam = Exam.query.filter(Exam.exam_id==exam_id).first()
        exam1=exam.exam_name

        
        # Seaborn Theme
        
        sns.set_theme(style="white")

        
        # Create Figure
        
        fig, ax = plt.subplots(figsize=(12,6))

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

        df=pd.DataFrame({"Exam":[exa.exam_name for exa in exam_all],"Marks":[m.marks for m in mark]})
        
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

        plt.ylim(0,100)

        sns.despine(left=False, bottom=False)

        plt.tight_layout()
        buffer = BytesIO()

        plt.savefig(buffer, format="png")

        buffer.seek(0)

        graph = base64.b64encode(buffer.getvalue()).decode()

        plt.close()

        return render_template("graph.html", graph=graph) 

@app.route("/about")
def about():
    return render_template("about_us.html")

@app.route("/support")
def support():
    return render_template("support.html")
    
@app.route("/profile")
def profile():
    return render_template("profile.html",username=session.get("username","").removesuffix("@gmail.com"))

@app.route("/log-out", methods=["POST", "GET"])
def log_out():
    app.logger.info(f"{session.get("username","")} has logged out")
    session.clear()
    return redirect(url_for("login_page"))

@app.route("/loading")
def loading():
    """Shown immediately after the user clicks 'Send Results'.
    This page's JS fires the actual /send_results request in the background
    and then redirects to /success or /error_page once it finishes."""
    sub = request.args.get("sub", "")
    exa = request.args.get("exam", "")
    return render_template("loading.html", sub=sub, exam=exa)


@app.route("/success")
def success():
    sent_count = request.args.get("sent", "0")
    sub = request.args.get("sub", "")
    exa = request.args.get("exam", "")
    app.logger.info(f"{session.get("username","")} susccesfully sent emails")
    return render_template("success.html", sent_count=sent_count, sub=sub, exam=exa)


@app.route("/error_page")
def error_page():
    msg = request.args.get("msg", "Something went wrong while sending results.")
    app.logger.error("Something went wrong while sending results.")
    return render_template("Error.html", data=msg, location="/data")


@app.route("/send_results", methods=["POST"])
def send_results():
    """Called via fetch() from loading.html. Returns JSON, not HTML,
    so the loading page's JS can decide where to redirect next."""
    PASSWORD = dict_details.get(session.get("username", ""))
    if not PASSWORD:
        return jsonify({"status": "error", "message": "Could not find email credentials for this account."}), 400

    class_value = session.get("class_value")
    sec = session.get("sec")
    sub = request.form.get("subject10", "") or request.form.get("subject12", "")
    exa = request.form.get("exam10", "") or request.form.get("exam12", "")

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
                    app.logger.error(e)
                    return jsonify({"status": "error", "message": f"{e}\nContact the developer"}), 500

    return jsonify({"status": "success", "sent_count": sent_count})

@app.route("/leaderboard", methods=["GET", "POST"])
def leaderboard():
        exa = request.form.get("exam", "")
        class_value = session.get("class_value")
        sec = session.get("sec") 
        if exa:
                if class_value is not None:

                    students = Student.query.filter(
                        Student.student_class == class_value
                    ).all()

                    exam = Exam.query.filter(Exam.exam_name == exa).first() if exa else None

                    leaderboard =db.session.query(
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

                    return render_template("leaderboard.html",
                                class_value=class_value,
                                students=students,
                                total_marks=total_marks,
                                podium=podium,
                                sub="All",
                                exam=exa
                                )
        return render_template("leaderboard.html",class_value=session.get("class_value",""))
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)#False if deploying True