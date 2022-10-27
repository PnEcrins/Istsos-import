from flask import Blueprint, jsonify, g, request

from istsosimport.env import db
from istsosimport.db.models import Import, Mapping, ObservedProperty, Procedure
from istsosimport.schemas import ImportSchema, ProcedureSchema

blueprint = Blueprint("api", __name__, url_prefix="/api/<service>")


@blueprint.route("/procedures", methods=["GET"])
def get_procedures():
    procedure_schema = ProcedureSchema()
    procedures = g.session.query(Procedure).all()
    return jsonify([procedure_schema.dump(p) for p in procedures])

@blueprint.route("/mappings", methods=["POST"])
def post_mapping():
    data = request.get_json()
    print(data)
    for d in data:
        if d["name"] == "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601":
            continue
        observed_prop = ObservedProperty.query.filter_by(def_opr=d["name"])
        print(observed_prop)
        observed_prop = observed_prop.one()
        new_mapping = Mapping(
            name="Test",
            id_opr=observed_prop.id_opr,
            column_name=d["value"]
        )
        db.session.add(new_mapping)
    db.session.commit()
    return jsonify('YEP')

@blueprint.route("/test", methods=["GET"])
def bis():
    return 'YEP'



@blueprint.route("/imports", methods=["GET"])
def imports():
    params = request.args
    limit = params.get("length", 10, int)
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
