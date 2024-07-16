from marshmallow import (
    Schema,
    fields,
    INCLUDE
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


class DataQI(Schema):
    INVALID_QI = fields.Integer(load_default=0)
    DEFAULT_QI = fields.Integer(load_default=100)
    VALID_PROPERTY_QI = fields.Integer(load_default=200)
    VALID_STATION_QI = fields.Integer(load_default=210)

class AuthenticationConfig(Schema):
    PROVIDERS = fields.List(
        fields.Dict(), load_default=[]
    )

    DEFAULT_RECONCILIATION_GROUP_ID = fields.Integer()
    DEFAULT_PROVIDER_ID = fields.String(required=True)


class Config(Schema):
    SQLALCHEMY_DATABASE_URI = fields.String(
        required=True,
        validate=Regexp(
            "^postgresql:\/\/.*:.*@[^:]+:\w+\/\w+",
            error="Database uri is invalid ex: postgresql://monuser:monpass@server:port/db_name",
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = fields.Boolean(load_default=True)
    LOG_LEVEL = fields.String(load_default=20)
    SERVICE = fields.String(required=True)
    SECRET_KEY = fields.String(required=True)
    CELERY = fields.Nested(CeleryConfig)
    MAIL_CONFIG = fields.Nested(MailConfig)
    UPLOAD_FOLDER = fields.String(load_default=str(ROOT_DIR / "uploaded_files"))
    DATA_QI = fields.Nested(DataQI, load_default=DataQI().load({}))
    URL_APPLICATION = fields.String(required=True)
    LOCALE = fields.String()
    AUTHENTICATION = fields.Nested(
        AuthenticationConfig,
        unknown=INCLUDE
    )