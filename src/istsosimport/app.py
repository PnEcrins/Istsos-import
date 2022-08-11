import logging

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from istsosimport.config.config_parser import config
from istsosimport.env import db, ma, flask_mail, ROOT_DIR
from istsosimport.utils.celery import celery_app
from istsosimport.utils.logs import config_loggers

log = logging.getLogger()


def create_app():
    app = Flask(__name__)
    conf = config.copy()
    conf.update(config["MAIL_CONFIG"])
    app.config.update(conf)
    config_loggers(conf)
    app.config["UPLOAD_FOLDER"] = ROOT_DIR / "uploaded_files"

    flask_mail.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    celery_app.conf.update(app.config["CELERY"])
    # set from headers HTTP_HOST, SERVER_NAME, and SERVER_PORT
    app.config["SERVER_NAME"] = "127.0.0.1:5000"

    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)
    from istsosimport.routes.main import blueprint

    app.register_blueprint(blueprint)
    from istsosimport.routes.api import blueprint

    app.register_blueprint(blueprint, url_prefix="/api")

    return app
