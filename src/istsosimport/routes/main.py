from copy import copy
import csv
import datetime
import logging
import os

import pytz
from pathlib import Path

from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for,
    request,
    current_app,
    abort,
    current_app,
    g,
)
from werkzeug.utils import secure_filename
from werkzeug.datastructures import MultiDict


from istsosimport.env import db
from istsosimport.db.models import Import, ObservedProperty, Procedure
from istsosimport.schemas import ImportSchema, ObservedProperySchema, ProcedureSchema
from istsosimport.config.config_parser import config

from istsosimport.tasks import import_data


blueprint = Blueprint("main", __name__)

log = logging.getLogger()


@blueprint.route("/<service>/imports", methods=["GET"])
def imports():
    return render_template("import-list.html")


@blueprint.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "GET":
        procedures = db.session.query(Procedure).all()
        schema = ProcedureSchema()
        return render_template(
            "upload.html",
            procedures=[schema.dump(p) for p in procedures],
            timezones=list(pytz.all_timezones),
        )
    else:
        f = request.files["file"]
        data = MultiDict(request.form)
        data["service"] = config["SERVICE"]
        filename = secure_filename(f"{datetime.datetime.now()}-{f.filename}")
        data["file_name"] = filename
        if data["timezone"] == "null":
            data["timezone"] = None
        imp = ImportSchema().load(data=data, session=db.session)
        db.session.add(imp)
        db.session.commit()
        new_id_import = imp.id_import
        db.session.commit()
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        f.save(path)
        return redirect(
            url_for(
                "main.mapping",
                service=config["SERVICE"],
                id_import=new_id_import,
            )
        )


@blueprint.route("/mapping/<int:id_import>/")
@blueprint.route("/mapping/<int:id_import>/<missing_cols>")
def mapping(id_import, missing_cols=[]):
    imp_schema = ImportSchema()
    imp = db.session.query(Import).get(id_import)
    import_as_dict = imp_schema.dump(imp)
    if missing_cols:
        missing_cols = missing_cols.split(",")
    path = Path(current_app.config["UPLOAD_FOLDER"], imp.file_name)
    if not path.exists():
        abort(404)
    in_columns_name = []
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=imp.delimiter)
        for row in csv_reader:
            in_columns_name = row
            break
    return render_template(
        "mapping.html",
        id_import=id_import,
        in_columns_name=in_columns_name,
        procedure=import_as_dict["procedure"],
        missing_cols=missing_cols,
    )


@blueprint.route("/<int:id_import>/load", methods=["POST"])
def load(id_import):
    data = request.form.to_dict()
    imp = db.session.query(Import).get(id_import)
    csv_mapping = {}
    missing_cols = []
    # make a correct mapping in a dict between expected column name (observed_prop) and the csv given column names
    for observed_prop, csv_col in data.items():
        if csv_col == "null":
            missing_cols.append(observed_prop)
        csv_mapping[observed_prop] = csv_col
    # check if all observed properties have a correponding column in csv
    for proc in imp.procedure.proc_obs:
        if not proc.observed_property.def_opr in data.keys():
            missing_cols.append(proc.observed_property.def_opr)
    if missing_cols:
        return redirect(
            url_for(
                "main.mapping",
                service=config["SERVICE"],
                id_import=id_import,
                missing_cols=",".join(missing_cols),
            )
        )

    import_data(
        import_dict=ImportSchema().dump(imp),
        filename=imp.file_name,
        separator=imp.delimiter,
        config=config,
        csv_mapping=csv_mapping,
        service=config["SERVICE"],
    )

    return redirect(url_for("main.processing"))


@blueprint.route("/processing")
def processing():
    return render_template("import_processing.html")
