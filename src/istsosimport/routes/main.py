import csv
import datetime
from email.mime import base
import json
import logging
import os

from pathlib import Path

import pandas as pd
import requests as req
from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for,
    request,
    current_app,
    abort,
    current_app,
    session,
)
from werkzeug.utils import secure_filename

from istsosimport.env import db
from istsosimport.db.models import ObservedProperty, Procedure
from istsosimport.schemas import ObservedProperySchema, ProcedureSchema
from istsosimport.config.config_parser import config

from istsosimport.tasks import run_insert_observation_api


blueprint = Blueprint("main", __name__)

log = logging.getLogger()


@blueprint.route("/", methods=["GET"])
def home():
    current_app.logger.debug("OHHH")
    db.session.connection(
        execution_options={"schema_translate_map": {"per_service": "ecrins"}}
    )
    data = db.session.query(Procedure).all()
    procedure_schema = ProcedureSchema()
    for d in data:
        s = procedure_schema.dump(d)
    return render_template("home.html")


@blueprint.route("/upload", methods=["GET", "POST"])
def upload():
    # db.session.connection(
    #     execution_options={"schema_translate_map": {"per_service": "ecrins"}}
    # )
    if request.method == "GET":
        return render_template(
            "import.html", services=current_app.config["SOS_SERVICES"]
        )
    else:
        f = request.files["file"]
        data = request.form
        session["separator"] = data["separator"]
        session["mail_recipient"] = data["mail_recipient"]
        id_prc = data.get("procedure")
        filename = secure_filename(f"{datetime.datetime.now()}-{f.filename}")
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        f.save(path)
        return redirect(url_for("main.mapping", id_prc=id_prc, filename=filename))


@blueprint.route("/<service>/mapping/<int:id_prc>/<filename>")
@blueprint.route(
    "/<service>/mapping/<int:id_prc>/<filename>/missing_cols/<missing_cols>"
)
def mapping(id_prc, filename, missing_cols=[]):
    if missing_cols:
        missing_cols = missing_cols.split(",")
    db.session.connection(
        execution_options={"schema_translate_map": {"per_service": "ecrins"}}
    )
    path = Path(current_app.config["UPLOAD_FOLDER"], filename)
    if not path.exists():
        abort(404)
    in_columns_name = []
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=session.get("separator"))
        for row in csv_reader:
            in_columns_name = row
            break
    db.session.connection(
        execution_options={"schema_translate_map": {"per_service": "ecrins"}}
    )
    observed_properties = db.session.query(ObservedProperty).all()
    observed_property_schema = ObservedProperySchema()
    procedure = db.session.query(Procedure).get(id_prc)
    return render_template(
        "mapping.html",
        procedure=ProcedureSchema().dump(procedure),
        in_columns_name=in_columns_name,
        observed_properties=[
            observed_property_schema.dump(o) for o in observed_properties
        ],
        filename=filename,
        missing_cols=missing_cols,
    )


@blueprint.route("/<service>/load", methods=["POST"])
def load():
    db.session.connection(
        execution_options={"schema_translate_map": {"per_service": "ecrins"}}
    )
    data = request.form.to_dict()
    id_prc = int(data.pop("id_prc"))
    filename = data.pop("filename")

    procedure = db.session.query(Procedure).get(id_prc)
    serialize_procedure = ProcedureSchema().dump(procedure)
    # get last obs to have the structure of a posted data
    last_obs = procedure.getlastobservation("ecrins", "temporary", serialize_procedure)

    csv_mapping = {}
    # make a correct mapping in a dict between expected column name (observed_prop) and the csv given column names
    for in_col, out_col in data.items():
        csv_mapping[out_col] = in_col

    # get the observerd property in the correct order from the getObservation API
    out_ordered_columns = list(
        map(lambda c: c["definition"], last_obs["result"]["DataArray"]["field"])
    )
    # reorder the csv columns according to the observed property order
    in_ordered_columns = []
    missing_cols = []
    # order in columns and check if all columns of prodecure has a corespondance
    for col in out_ordered_columns:
        if col.split(":")[-1] == "qualityIndex" and col not in csv_mapping.keys():
            csv_mapping[col] = col
        try:
            temp_col = csv_mapping[col]
        except KeyError:
            missing_cols.append(col)
        in_ordered_columns.append(temp_col)
    if missing_cols:
        return redirect(
            url_for(
                "main.mapping",
                id_prc=id_prc,
                filename=filename,
                missing_cols=",".join(missing_cols),
            )
        )
    base_url = request.base_url
    run_insert_observation_api.delay(
        filename,
        in_ordered_columns,
        out_ordered_columns,
        csv_mapping,
        last_obs,
        serialize_procedure,
        config,
        session.get("mail_recipient"),
        session.get("separator"),
        base_url,
    )

    return redirect(url_for("main.processing"))


@blueprint.route("/processing")
def processing():
    return render_template("import_processing.html")
