from app.extensions import db


class Admin(db.Model):
    __tablename__ = "Admin"

    Gmail = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(255), nullable=False)
