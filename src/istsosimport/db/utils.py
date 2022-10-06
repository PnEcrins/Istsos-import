from sqlalchemy.orm import Session

from istsosimport.env import db


def get_schema_session(schema):
    return Session(
        bind=db.session.connection().execution_options(
            schema_translate_map={"per_service": schema}
        )
    )
