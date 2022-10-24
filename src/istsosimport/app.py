import logging
import os

from urllib.parse import urlparse
from flask import Flask, g
from sqlalchemy.orm import Session
from werkzeug.middleware.proxy_fix import ProxyFix

from istsosimport.config.config_parser import config
from istsosimport.env import db, ma, flask_mail, ROOT_DIR, migrate
from istsosimport.utils.celery import celery_app
from istsosimport.utils.logs import config_loggers

log = logging.getLogger()


def create_app():
    app = Flask(__name__)
    url_app = urlparse(config["URL_APPLICATION"])
    app.config["APPLICATION_ROOT"] = url_app.path
    app.config["PREFERRED_URL_SCHEME"] = url_app.scheme
    if "SCRIPT_NAME" not in os.environ:
        os.environ["SCRIPT_NAME"] = app.config["APPLICATION_ROOT"].rstrip("/")
    conf = config.copy()
    conf.update(config["MAIL_CONFIG"])
    app.config.update(conf)
    config_loggers(conf)
    app.config["UPLOAD_FOLDER"] = ROOT_DIR / "uploaded_files"

    flask_mail.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    celery_app.conf.update(app.config["CELERY"])

    # flask admin
    app.config["FLASK_ADMIN_SWATCH"] = "simplex"
    app.config["FLASK_ADMIN_FLUID_LAYOUT"] = True
    from istsosimport.admin import admin

    admin.init_app(app)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)
    from istsosimport.routes.main import blueprint

    app.register_blueprint(blueprint)
    from istsosimport.routes.api import blueprint

    app.register_blueprint(blueprint)

    return app
