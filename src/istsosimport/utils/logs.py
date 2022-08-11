import logging
import os
from flask.logging import default_handler

def config_loggers(config):
    """
    Configuration des niveaux de logging/warnings
    et des hanlers
    """
    root_logger = logging.getLogger()
    root_logger.addHandler(default_handler)
    root_logger.setLevel(config["LOG_LEVEL"])
    if not os.environ.get("FLASK_ENV") == "development":
        gunicorn_error_logger = logging.getLogger("gunicorn.error")
        root_logger.handlers.extend(gunicorn_error_logger.handlers)