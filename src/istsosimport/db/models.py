import requests

from sqlalchemy import  ForeignKey
from flask import current_app
from werkzeug.exceptions import HTTPException

from istsosimport.env import db


proc_obs = db.Table(
    "proc_obs",
    db.Column("id_pr", primary_key=True),
    db.Column("id_prc_fk", db.Integer, db.ForeignKey("procedures.id_prc")),
    db.Column("id_opr_fk", db.Integer, db.ForeignKey("observed_properties.id_opr")),
    schema="per_service",
)

class ObservedProperty(db.Model):
    __tablename__ = "observed_properties"
    __table_args__ = {"schema": "per_service"}
    id_opr = db.Column(db.Integer, primary_key=True)
    name_opr = db.Column(db.Unicode)
    def_opr = db.Column(db.Unicode)
    desc_opr = db.Column(db.Unicode)
    constr_opr = db.Column(db.Unicode)

class Procedure(db.Model):
    __tablename__ = "procedures"
    __table_args__ = {"schema": "per_service"}
    id_prc = db.Column(db.Integer, primary_key=True)
    assignedid_prc = db.Column(db.Unicode)
    name_prc = db.Column(db.Unicode)
    observed_properties = db.relationship(
        ObservedProperty,
        secondary=proc_obs,
        primaryjoin=(id_prc == proc_obs.c.id_prc_fk),
        secondaryjoin=(proc_obs.c.id_opr_fk == ObservedProperty.id_opr),
        foreign_keys=[proc_obs.c.id_prc_fk, proc_obs.c.id_opr_fk],
        lazy="joined"
    )

    def getlastobservation(self, service, offering, serialize_procedure):
        
        url = """{url}/wa/istsos/services/{service}/operations/getobservation/
                offerings/{offering}/procedures/{procedure}/observedproperties/{opr}/eventtime/last"
            """.format(
                url=current_app.config["ISTSOS_API_URL"],
                service=service,
                offering=offering,
                procedure=self.name_prc,
                opr=",".join(map(lambda o : o["def_opr"] , serialize_procedure["observed_properties"]))

            )
        url = "http://localhost/istsos/wa/istsos/services/ecrins/operations/getobservation/offerings/temporary/procedures/STATION_HYDRO_LAUVITEL/observedproperties/urn:ogc:def:parameter:x-istsos:1.0:time:iso8601,urn:ogc:def:parameter:x-istsos:1.0:river:water:height/eventtime/last"
        res = requests.get(url)
        data = res.json()
        if data['success'] is False:
            raise HTTPException(
                f"IstSOS api fail - {data['message']}"
            )
        else:
            return data["data"][0]
        

#  http://localhost/istsos/wa/istsos/services/ecrins/operations/getobservation/offerings/temporary/procedures/STATION_HYDRO_LAUVITEL/observedproperties/urn:ogc:def:parameter:x-istsos:1.0:time:iso8601,urn:ogc:def:parameter:x-istsos:1.0:river:water:height/eventtime/last

    def to_import_json(self, force_insert=True):
        d = {
            "ForceInsert": force_insert, 
            "AssignedSensorId": self.assignedid_prc, "Observation": {"name": "STATION_HYDRO_LAUVITEL", "samplingTime": {"beginPosition": "2016-11-13T03:00:00Z", "endPosition": "2016-11-13T08:00:00Z"}, "procedure": "urn:ogc:def:procedure:x-istsos:1.0:STATION_HYDRO_LAUVITEL", "observedProperty": {"CompositePhenomenon": {"id": "comp_1", "dimension": "3", "name": "timeSeriesOfObservations"}, "component": ["urn:ogc:def:parameter:x-istsos:1.0:time:iso8601", "urn:ogc:def:parameter:x-istsos:1.0:river:water:height", "urn:ogc:def:parameter:x-istsos:1.0:river:water:height:qualityIndex"]}, "featureOfInterest": {"name": "urn:ogc:def:feature:x-istsos:1.0:Point:Lauvitel", "geom": "<gml:Point srsName='EPSG:4326'><gml:coordinates>5,44,150</gml:coordinates></gml:Point>"}, "result": {"DataArray": {"elementCount": "3", "field": [{"name": "Time", "definition": "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"}, {"name": "river-height", "definition": "urn:ogc:def:parameter:x-istsos:1.0:river:water:height", "uom": "m"}, {"name": "river-height:qualityIndex", "definition": "urn:ogc:def:parameter:x-istsos:1.0:river:water:height:qualityIndex", "uom": "-"}], "values": [["2016-11-13T03:00:00Z", "16.081", "100"], ["2016-11-13T04:00:00Z", "16.076", "100"], ["2016-11-13T05:00:00Z", "16.075", "100"], ["2016-11-13T06:00:00Z", "16.076", "100"], ["2016-11-13T07:00:00Z", "16.075", "100"]]}}, "AssignedSensorId": "a7ace3a0130711ed8c9675c701a63958"}}




