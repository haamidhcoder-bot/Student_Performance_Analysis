"""Application logging setup.

Extracted verbatim from the original app.py so the log format, rotation
policy, and level are unchanged.
"""
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = RotatingFileHandler(
        "Management App.log",
        maxBytes=1024 * 1024,  # 1 MB
        backupCount=5
    )

    handler.setFormatter(formatter)

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
