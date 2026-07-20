"""Shared Flask extension instances.

Kept in their own module (instead of app/__init__.py) so that model files
and service files can import `db` without triggering a circular import with
the application factory.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
