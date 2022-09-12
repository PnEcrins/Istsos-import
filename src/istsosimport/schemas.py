from dataclasses import field
from marshmallow import fields, post_dump
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from istsosimport.db.models import Procedure, ObservedProperty, ProcObs


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

    # @post_dump(pass_many=True)
    # def add_missing_time_prop(self, data, **kwargs):
    #     data["observed_properties"].append(
    #         {
    #             "def_opr": "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601",
    #             "name_opr": "Date format iso 8601",
    #         }
    #     )
    #     return data
