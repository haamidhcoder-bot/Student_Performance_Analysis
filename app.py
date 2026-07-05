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
    subject=db.Column(db.String(10))
    marks=db.column(db.Integer)

    def __repr__(self):
        return f"<Student {self.roll_no} - {self.student_name}>"


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

@app.route("/data", methods=["GET", "POST"])
def data():
    if request.method == "POST":
        class_value = request.form.get("class", "").strip()
        sec = request.form.get("section", "").strip()

        if class_value:
            class_value = int(class_value)
            students = Student.query.filter(
                Student.student_class == class_value,
                Student.section == sec
            ).all()

            if students:
                return render_template("Student_data.html", class_value=class_value,students=students)

        return render_template("Home.html", error="No matching students found.")

    return render_template("Home.html")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)