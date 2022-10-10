from dataclasses import Field
import os
from marshmallow import (
    Schema,
    fields,
)

from marshmallow.validate import Regexp
from istsosimport.env import ROOT_DIR


class CeleryConfig(Schema):
    broker_url = fields.String()
    result_backend = fields.String(required=False)


class MailConfig(Schema):
    MAIL_SERVER = fields.String(required=True)
    MAIL_PORT = fields.Integer(required=True)
    MAIL_USE_TLS = fields.Boolean()
    MAIL_USE_SSL = fields.Boolean()
    MAIL_USERNAME = fields.String(required=True)
    MAIL_PASSWORD = fields.String(required=True)
    MAIL_DEFAULT_SENDER = fields.String()
    MAIL_MAX_EMAILS = fields.Integer()
    MAIL_SUPPRESS_SEND = fields.Boolean()
    MAIL_ASCII_ATTACHMENTS = fields.Boolean()


class Config(Schema):
    SQLALCHEMY_DATABASE_URI = fields.String(
        required=True,
        validate=Regexp(
            "^postgresql:\/\/.*:.*@[^:]+:\w+\/\w+",
            error="Database uri is invalid ex: postgresql://monuser:monpass@server:port/db_name",
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = fields.Boolean(load_default=True)
    ISTSOS_API_URL = fields.String(required=True)
    LOG_LEVEL = fields.String(load_default=20)
    SERVICE = fields.String(required=True)
    SECRET_KEY = fields.String(required=True)
    CELERY = fields.Nested(CeleryConfig)
    MAIL_CONFIG = fields.Nested(MailConfig)
    UPLOAD_FOLDER = fields.String(load_default=str(ROOT_DIR / "uploaded_files"))
    SOS_SERVICES = fields.List(fields.String, required=True)
    SERVER_NAME = fields.String(required=True)
