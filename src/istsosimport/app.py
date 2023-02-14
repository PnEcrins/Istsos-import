import locale
import logging
import os

from urllib.parse import urlparse

from flask import Flask, g, session

# from flask_login import LoginManager, login_manager
# from flask_ldap3_login import LDAP3LoginManager

from werkzeug.middleware.proxy_fix import ProxyFix

from istsosimport.config.config_parser import config
from istsosimport.env import db, ma, flask_mail, ROOT_DIR, migrate, oidc
from istsosimport.auth import login_manager
from istsosimport.utils.celery import celery_app
from istsosimport.utils.logs import config_loggers
from istsosimport.db.models import User

# from istsosimport.db.models import User

log = logging.getLogger()


def set_locale(config):
    server_locale = locale.getdefaultlocale()
    locale.setlocale(locale.LC_NUMERIC, config.get("LOCALE", server_locale))


def create_app():
    app = Flask(__name__)
    conf = config.copy()
    set_locale(config)
    conf.update(config["MAIL_CONFIG"])
    app.config.update(conf)
    url_app = urlparse(config["URL_APPLICATION"])
    app.config["APPLICATION_ROOT"] = url_app.path
    app.config["PREFERRED_URL_SCHEME"] = url_app.scheme
    app.config["SERVER_NAME"] = url_app.netloc
    if "SCRIPT_NAME" not in os.environ:
        os.environ["SCRIPT_NAME"] = app.config["APPLICATION_ROOT"].rstrip("/")
    config_loggers(conf)
    app.config["UPLOAD_FOLDER"] = ROOT_DIR / "uploaded_files"

    flask_mail.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    celery_app.conf.update(app.config["CELERY"])

    login_manager.init_app(app)

    app.config.update(
        {
            "OIDC_CLIENT_SECRETS": "client_secrets.json",
            "OIDC_ID_TOKEN_COOKIE_SECURE": False,
            "OIDC_REQUIRE_VERIFIED_EMAIL": False,
            "OIDC_USER_INFO_ENABLED": True,
            # "OIDC_OPENID_REALM": "master",
            "OIDC_SCOPES": ["openid", "email", "profile"],
            "OIDC_INTROSPECTION_AUTH_METHOD": "client_secret_post",
        }
    )
    if config["OIDC_AUTHENT"]:
        oidc.init_app(app)

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

    from istsosimport.routes.auth import blueprint

    app.register_blueprint(blueprint=blueprint, url_prefix="/auth")
    return app
