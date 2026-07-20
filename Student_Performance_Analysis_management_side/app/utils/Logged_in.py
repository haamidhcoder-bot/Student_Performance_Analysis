from functools import wraps
from flask import session, redirect, url_for

def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("auth.login"))

        return function(*args, **kwargs)

    return wrapper