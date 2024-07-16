import json
import uuid
from sqlalchemy import ForeignKey
from sqlalchemy import func, select
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID

# for migration
from pypnusershub.db.models import *

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
    stime_prc = db.Column(db.DateTime)
    etime_prc = db.Column(db.DateTime)
    proc_obs = db.relationship(
        "ProcObs",
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

    id_msr = db.Column(db.Integer, primary_key=True)
    id_eti_fk = db.Column(db.Integer, db.ForeignKey(EventTime.id_eti))
    id_pro_fk = db.Column(db.Integer, db.ForeignKey(ProcObs.id_pro))
    id_qi_fk = db.Column(db.Integer)
    val_msr = db.Column(db.Float)
    proc_obs = db.relationship(
        "ProcObs", primaryjoin=("Measure.id_pro_fk == ProcObs.id_pro"), lazy="joined"
    )
    event_time = db.relationship("EventTime", back_populates="measures")

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
        # if not constraint at station level and property leve set DEFAULT QI
        if (
            not proc_obs["constr_pro"]
            and not proc_obs["observed_property"]["constr_opr"]
        ):
            self.id_qi_fk = config["DATA_QI"]["DEFAULT_QI"]
            return

        # if at least on check, check as invalid before tests
        else:
            self.id_qi_fk = config["DATA_QI"]["INVALID_QI"]

        # first check at property level
        self._set_qi(
            quality_constainst=proc_obs["observed_property"]["constr_opr"],
            valid_qi_constant=config["DATA_QI"]["VALID_PROPERTY_QI"],
        )
        # check at station level
        self._set_qi(
            quality_constainst=proc_obs["constr_pro"],
            valid_qi_constant=config["DATA_QI"]["VALID_STATION_QI"],
        )

    def _set_qi(self, quality_constainst, valid_qi_constant):
        if quality_constainst is None:
            return
        else:
            quality_constainst = json.loads(quality_constainst)
        if "min" in quality_constainst:
            checker = float(quality_constainst["min"])
            if self.val_msr >= checker:
                self.id_qi_fk = valid_qi_constant
        elif "max" in quality_constainst:
            checker = float(quality_constainst["max"])
            if self.val_msr <= checker:
                self.id_qi_fk = valid_qi_constant
        elif "interval" in quality_constainst:
            checker = quality_constainst["interval"]
            if self.val_msr >= float(checker[0]) and self.val_msr <= float(checker[1]):
                self.id_qi_fk = valid_qi_constant
        elif "valueList" in quality_constainst:
            if self.val_msr in list(
                map(lambda v: float(v), quality_constainst["valueList"])
            ):
                self.id_qi_fk = valid_qi_constant


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
    timezone = db.Column(db.Unicode)
    timezone = db.Column(db.Unicode)

    procedure = db.relationship(Procedure, lazy="joined")


