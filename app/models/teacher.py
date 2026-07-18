from app.extensions import db


class Teacher(db.Model):
    __tablename__ = "teachers"

    Gmail = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
