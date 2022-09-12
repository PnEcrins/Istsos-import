import csv
from datetime import date, datetime
import os
import json
import logging

import pandas as pd
import requests as req
import isodate

from flask import render_template, g
from sqlalchemy import exc

from istsosimport.utils.celery import celery_app
from istsosimport.utils.mail import send_mail
from istsosimport.env import FILE_ERROR_DIRECTORY, db
from istsosimport.db.models import EventTime, Measure, Procedure


log = logging.getLogger()


@celery_app.task(bind=True)
def import_data(self, id_prc, filename, separator, config, csv_mapping):
    procedure = g.session.query(Procedure).get(id_prc)
    with open(os.path.join(config["UPLOAD_FOLDER"], filename)) as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=separator)
        for row in csvreader:
            date_col = csv_mapping["urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"]
            eventtime = EventTime(
                procedure=procedure, time_eti=isodate.parse_datetime(row[date_col])
            )
            for proc in procedure.proc_obs:
                val_col = csv_mapping[proc.observed_property.def_opr]
                try:
                    floated_value = float(row[val_col])
                except Exception as e:
                    print(e)
                measure = Measure(val_msr=floated_value, proc_obs=proc)
                eventtime.measures.append(measure)
                g.session.add(eventtime)
            try:
                g.session.commit()
            except exc.SQLAlchemyError as e:
                log.error("ROLLBACK")
                log.error(e)
                g.session.rollback()
