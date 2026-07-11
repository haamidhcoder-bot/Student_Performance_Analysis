from flask import Flask,render_template,redirect,request,session
from flask_sqlalchemy import SQLAlchemy
import mysql.connector as sql
from sqlalchemy import func

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

    username = db.Column(db.String(50), primary_key=True)
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
            teachers=Teacher.query.filter(
                Teacher.username==user_n,
                Teacher.password==pass_n
            ).first()
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


@app.route("/delete/<int:roll_no>")
def delete(roll_no:int):
    delete_student=Student.query.get_or_404(roll_no)
    try:
        db.session.delete(delete_student)#deleting data
        db.session.commit()#commiting it
        return redirect("/data")#back to home
    except Exception as e:
        print(f"ERROR {e}")
        return redirect("/data")


@app.route("/edit/<int:roll_no>/<string:subject>", methods=["POST", "GET"])
def edit(roll_no:int, subject:str):
    mark=Mark.query.filter(
        Mark.roll_no==roll_no,
        Mark.subject==subject
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
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)