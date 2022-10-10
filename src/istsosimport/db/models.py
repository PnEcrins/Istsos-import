from datetime import datetime
import json
import requests

from sqlalchemy import ForeignKey
from flask import current_app
from sqlalchemy import orm, func
from werkzeug.exceptions import HTTPException

from istsosimport.env import db
from istsosimport.config.config_parser import config


class ObservedProperty(db.Model):
    __tablename__ = "observed_properties"
    __table_args__ = {"schema": config["SERVICE"]}
    id_opr = db.Column(db.Integer, primary_key=True)
    name_opr = db.Column(db.Unicode)
    def_opr = db.Column(db.Unicode)
    desc_opr = db.Column(db.Unicode)
    constr_opr = db.Column(db.Unicode)


class Procedure(db.Model):
    __tablename__ = "procedures"
    __table_args__ = {"schema": config["SERVICE"]}
    id_prc = db.Column(db.Integer, primary_key=True)
    assignedid_prc = db.Column(db.Unicode)
    name_prc = db.Column(db.Unicode)
    proc_obs = db.relationship(
        "ProcObs",
        # primaryjoin="Procedure.id_opr_fk == ObservedProperty.id_opr",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return self.name_prc


class ProcObs(db.Model):
    __tablename__ = "proc_obs"
    __table_args__ = {"schema": config["SERVICE"]}
    id_pro = db.Column(db.Integer, primary_key=True)
    id_opr_fk = db.Column(db.Integer, db.ForeignKey(ObservedProperty.id_opr))
    constr_pro = db.Column(db.Unicode)
    id_prc_fk = db.Column(db.Integer, db.ForeignKey(Procedure.id_prc))
    observed_property = db.relationship(
        "ObservedProperty",
        primaryjoin="ProcObs.id_opr_fk == ObservedProperty.id_opr",
        lazy="joined",
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
    __table_args__ = {"schema": config["SERVICE"]}
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
    __table_args__ = {"schema": config["SERVICE"]}
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

    #### TODO : quality index coul be at obs property level ...
    def set_quality(self, proc_obs):
        """
        Set the quality index with the given quality constraint
        If no constraint -> set Measure.DEFAULT_QI
        If valid constraint -> set Measure.VALID_QI
        If invalid constraint -> set Measure.INVALID_QI

        HACK : quality could be set with a Measure object
        without a loaded proc_obs relationship
        so it take proc_obs as dict in parameter
        """
        if not proc_obs["constr_pro"]:
            self.id_qi_fk = Measure.DEFAULT_QI
        else:
            self.id_qi_fk = Measure.INVALID_QI
            quality_constainst = json.loads(proc_obs["constr_pro"])
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


class Import(db.Model):
    __tablename__ = "imports"
    __table_args__ = {"schema": "public"}
    id_import = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.Unicode)
    date_import = db.Column(db.DateTime, server_default=func.now())
    email = db.Column(db.Unicode)
    id_prc = db.Column(db.Integer, ForeignKey(Procedure.id_prc))
    nb_row_total = db.Column(db.Integer)
    nb_row_inserted = db.Column(db.Integer)
    error_file = db.Column(db.Unicode)
    delimiter = db.Column(db.Unicode)
    service = db.Column(db.Unicode, nullable=False)

    procedure = db.relationship(Procedure, lazy="joined")
