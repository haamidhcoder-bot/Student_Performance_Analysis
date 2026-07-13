#pip install -r requirements.txt
from flask import Flask,render_template,redirect,request,session
from flask_sqlalchemy import SQLAlchemy
import mysql.connector as sql
from sqlalchemy import func
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

cn = sql.connect(host='127.0.0.1', user='root', password="pass12345")
cr = cn.cursor()
cr.execute("create database if not exists schooldb")


app=Flask(__name__)


app.secret_key = "some-random-secret-string"  # required for sessions to work

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:pass12345@localhost/schooldb"#format for using mysql
)

db = SQLAlchemy(app)

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
            remember=request.form.get("remember","")
            teachers=Teacher.query.filter(
                Teacher.Gmail==user_n,
                Teacher.password==pass_n
            ).first()
            """if remember:
                session[user_n]=pass_n"""
            if teachers:
                return render_template("Home.html")
            else:
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
                return render_template("Home.html", error="Invalid class value.")
            session["class_value"] =class_value
            session["sec"]=sec
            students = Student.query.filter(
                Student.student_class == class_value,
                Student.section == sec
            ).all()
            if students:
                return render_template("Student_data.html", class_value=class_value,sub="")

        return render_template("Home.html", error="No matching students found.")

    return render_template("Home.html")

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
                "Student_data.html",
                class_value=class_value,
                students=students,
                total_marks=total_marks,
                sub=sub,
                exam=exa
            )

        if sub and exa:
            return render_template(
                "Student_data.html",
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
            db.session.commit()#commiting it
            return redirect("/data")#back to home
        except Exception as e:
            print(f"ERROR {e}")
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
        plt.show()

        return render_template("Student_data.html", 
                               class_value=session.get("class_value"),
                               students=students,
                               results=res,
                               sub=subject,
                               exam=exam1) 

@app.route("/about")
def about():
    return render_template("about_us.html")

@app.route("/support")
def support():
    return render_template("support.html")
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)