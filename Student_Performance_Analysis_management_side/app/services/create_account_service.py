import re

from app.models.Administration import Admin
from app.extensions import db

def create_account(user,password,confirm_password):
    pattern="^(?=.*[0-9])"
    if password==confirm_password and re.match(pattern,password):
        new_admin=Admin(Gmail=user,password=password)
        try:
           db.session.add(new_admin)
           db.session.commit()
        except Exception as e:
           print(f'ERROR:{e}')
           return ""
    return True