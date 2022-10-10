import os
import datetime

import pandas as pd

from flask import Blueprint, jsonify, g, request

from istsosimport.env import db
from istsosimport.db.models import Import, Procedure
from istsosimport.schemas import ImportSchema, ProcedureSchema

blueprint = Blueprint("api", __name__, url_prefix="/api/<service>")


@blueprint.route("/procedures", methods=["GET"])
def get_procedures():
    procedure_schema = ProcedureSchema()
    procedures = g.session.query(Procedure).all()
    return jsonify([procedure_schema.dump(p) for p in procedures])


@blueprint.route("/imports", methods=["GET"])
def imports():
    params = request.args
    limit = params.get("limit", 10, int)
    start = params.get("start", 1, int)
    result = (
        g.session.query(Import).filter_by(service=g.service).limit(limit).offset(start)
    )
    import_schema = ImportSchema()
    nb_row_total = g.session.query(Import).count()
    return jsonify(
        {
            "recordsTotal": nb_row_total,
            "recordsFiltered": nb_row_total,
            "data": [import_schema.dump(imp) for imp in result],
        }
    )
