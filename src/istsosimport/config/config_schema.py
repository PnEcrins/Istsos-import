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


class DataQI(Schema):
    INVALID_QI = fields.Integer(load_default=0)
    DEFAULT_QI = fields.Integer(load_default=100)
    VALID_PROPERTY_QI = fields.Integer(load_default=200)
    VALID_STATION_QI = fields.Integer(load_default=210)


class LDAPConfig(Schema):
    LDAP_HOST = fields.String(required=True)
    LDAP_BASE_DN = fields.String(required=True)
    LDAP_USER_LOGIN_ATTR = fields.String(load_default="mail")
    LDAP_BIND_USER_DN = fields.String(required=True)
    LDAP_BIND_USER_PASSWORD = fields.String(required=True)
    LDAP_USER_RDN_ATTR = fields.String(load_default="cn")
    LDAP_USER_OBJECT_FILTER = fields.String(load_default="(objectclass=user)")
    LDAP_USER_SEARCH_SCOPE = fields.String(load_default="SUBTREE")


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
    OIDC_AUTHENT = fields.Boolean()
    LDAP_CONFIG = fields.Nested(LDAPConfig)
