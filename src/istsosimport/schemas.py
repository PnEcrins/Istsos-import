from dataclasses import field
from marshmallow import fields, post_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from istsosimport.db.models import Import, Procedure, ObservedProperty, ProcObs


class ObservedProperySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ObservedProperty
        load_instance = True
        include_relationships = True


class ProcObsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ProcObs
        load_instance = True
        include_relationships = True

    observed_property = fields.Nested(ObservedProperySchema)


class ProcedureSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Procedure
        include_relationships = True
        load_instance = True

    proc_obs = fields.Nested(ProcObsSchema, many=True)


class ImportSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Import
        include_relationships = True
        include_fk = True
        load_instance = True

    procedure = fields.Nested(ProcedureSchema, dump_only=True)
