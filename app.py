from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import mysql.connector as sql

cn = sql.connect(host='127.0.0.1', user='root', password="pass12345")
cr = cn.cursor()
cr.execute("create database if not exists schooldb")


app=Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+pymysql://root:pass12345@localhost/schooldb"#format for using mysql
)

db = SQLAlchemy(app)

class Teacher(db.Model):
    __tablename__ = "teachers"

    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Teacher {self.username}>"



class Student(db.Model):
    __tablename__ = "students"

    roll_no = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_class = db.Column("class", db.Integer, nullable=False)
    section = db.Column(db.String(1), nullable=False)

    marks = db.relationship(
        "Mark",
        backref="student",
        cascade="all, delete",
        lazy=True
    )

    def __repr__(self):
        return f"<Student {self.roll_no} - {self.student_name}>"



class Exam(db.Model):
    __tablename__ = "exams"

    exam_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_name = db.Column(db.String(50), nullable=False)

    marks = db.relationship(
        "Mark",
        backref="exam",
        cascade="all, delete",
        lazy=True
    )

    def __repr__(self):
        return f"<Exam {self.exam_name}>"



class Mark(db.Model):
    __tablename__ = "marks"

    roll_no = db.Column(
        db.Integer,
        db.ForeignKey("students.roll_no", ondelete="CASCADE"),
        primary_key=True
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey("exams.exam_id", ondelete="CASCADE"),
        primary_key=True
    )

    subject = db.Column(db.String(50), primary_key=True)
    marks = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return (
            f"<Mark Roll:{self.roll_no} "
            f"Exam:{self.exam_id} "
            f"Subject:{self.subject} "
            f"Marks:{self.marks}>"
        )
@app.route("/",methods=["post","get"])
def login_page():    
        users=Teacher.query.all()
        if request.method=="POST":
            user_n=request.form.get("username")
            pass_n=request.form.get("password")
            for teacher in users:
                if teacher.username==user_n and teacher.password==pass_n:
                    return render_template("Home.html")
        return render_template("login_page.html")

@app.route("/Home",methods=["post","get"])
def Home():
    pass


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)