import json
import requests

from sqlalchemy import ForeignKey
from flask import current_app
from sqlalchemy import orm
from werkzeug.exceptions import HTTPException

from istsosimport.env import db


# proc_obs = db.Table(
#     "proc_obs",
#     db.Column("id_pro", primary_key=True),
#     db.Column("id_prc_fk", db.Integer, db.ForeignKey("procedures.id_prc")),
#     db.Column("id_opr_fk", db.Integer, db.ForeignKey("observed_properties.id_opr")),
#     schema="per_service",
# )

# class ProcObs(db.Model):
#     __tablename__ = "proc_obs"
#     __table_args__ = {"schema": "per_service"}
#     id_pro = db.Column(db.Integer, primary_key=True)


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
    proc_obs = db.relationship(
        "ProcObs",
        # primaryjoin="Procedure.id_opr_fk == ObservedProperty.id_opr",
        lazy="joined",
    )


class ProcObs(db.Model):
    __tablename__ = "proc_obs"
    __table_args__ = {"schema": "per_service"}
    id_pro = db.Column(db.Integer, primary_key=True)
    id_opr_fk = db.Column(db.Integer, db.ForeignKey(ObservedProperty.id_opr))
    constr_pro = db.Column(db.Unicode)
    id_prc_fk = db.Column(db.Integer, db.ForeignKey(Procedure.id_prc))
    observed_property = db.relationship(
        "ObservedProperty",
        primaryjoin="ProcObs.id_opr_fk == ObservedProperty.id_opr",
    )

    def getlastobservation(self, service, offering, serialize_procedure):

        url = """{url}/wa/istsos/services/{service}/operations/getobservation/offerings/{offering}/procedures/{procedure}/observedproperties/{opr}/eventtime/last""".format(
            url=current_app.config["ISTSOS_API_URL"],
            service=service,
            offering=offering,
            procedure=self.name_prc,
            opr=",".join(
                map(lambda o: o["def_opr"], serialize_procedure["observed_properties"])
            ),
        )
        res = requests.get(url)
        data = res.json()
        if data["success"] is False:
            raise HTTPException(f"IstSOS api fail - {data['message']}")
        else:
            return data["data"][0]


class EventTime(db.Model):
    __tablename__ = "event_time"
    __table_args__ = {"schema": "per_service"}
    id_eti = db.Column(db.Integer, primary_key=True)
    id_prc_fk = db.Column(db.Integer, db.ForeignKey(Procedure.id_prc))
    time_eti = db.Column(db.DateTime)
    measures = db.relationship(
        "Measure",
        back_populates="event_time",
    )
    procedure = db.relationship(Procedure)


class Measure(db.Model):
    __tablename__ = "measures"
    __table_args__ = {"schema": "per_service"}
    VALID_QI = 200
    INVALID_QI = 0
    DEFAULT_QI = 100

    id_msr = db.Column(db.Integer, primary_key=True)
    id_eti_fk = db.Column(db.Integer, db.ForeignKey(EventTime.id_eti))
    id_pro_fk = db.Column(db.Integer, db.ForeignKey(ProcObs.id_pro))
    id_qi_fk = db.Column(db.Integer)
    val_msr = db.Column(db.Float)
    proc_obs = db.relationship(
        "ProcObs", primaryjoin=("Measure.id_pro_fk == ProcObs.id_pro"), lazy="joined"
    )
    event_time = db.relationship("EventTime", back_populates="measures")

    def __init__(self, **kwargs):
        super(Measure, self).__init__(**kwargs)
        self.__set_quality()

    #### TODO : quality index coul be at obs property level ...
    def __set_quality(self):
        """
        Set the quality index with the given quality constraint
        If no constraint -> set Measure.DEFAULT_QI
        If valid constraint -> set Measure.VALID_QI
        If invalid constraint -> set Measure.INVALID_QI
        """
        if not self.proc_obs.constr_pro:
            self.id_qi_fk = Measure.DEFAULT_QI
        else:
            self.id_qi_fk = Measure.INVALID_QI
            quality_constainst = json.loads(self.proc_obs.constr_pro)
            if "min" in quality_constainst:
                checker = quality_constainst["min"]
                if self.val_msr >= checker:
                    self.id_qi_fk = Measure.VALID_QI
            elif "max" in quality_constainst:
                checker = quality_constainst["max"]
                if self.val_msr <= checker:
                    self.id_qi_fk = Measure.VALID_QI
            elif "interval" in quality_constainst:
                checker = quality_constainst["interval"]
                if self.val_msr >= checker[0] and self.val_msr <= checker[1]:
                    self.id_qi_fk = Measure.VALID_QI
            elif "valueList" in quality_constainst:
                if self.val_msr in quality_constainst["valueList"]:
                    self.id_qi_fk = Measure.VALID_QI
