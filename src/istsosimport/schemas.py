import pytz

from dataclasses import field
from marshmallow import fields, post_dump, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from istsosimport.db.models import (
    Import,
    Procedure,
    ObservedProperty,
    ProcObs,
    EventTime,
)


class EvenTimeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EventTime
        load_instance = False
        include_fk = True

    @post_load(pass_original=True)
    def set_time_zone(elf, data, original_data, **kwargs):
        if data["time_eti"].tzinfo is None:
            target_timezone = pytz.timezone(original_data.get("timezone"))
            data["time_eti"] = target_timezone.localize(data["time_eti"])
        return data


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
