import os
import datetime

import pandas as pd

from flask import Blueprint, jsonify, g

from istsosimport.env import db
from istsosimport.db.models import Procedure
from istsosimport.schemas import ProcedureSchema

blueprint = Blueprint("api", __name__, url_prefix="/api/<service>")


@blueprint.route("/procedures", methods=["GET"])
def get_procedures():
    procedure_schema = ProcedureSchema()
    procedures = g.session.query(Procedure).all()
    return jsonify([procedure_schema.dump(p) for p in procedures])
