from contextlib import ExitStack
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
from sqlalchemy.orm import Session, joinedload
from istsosimport.schemas import ProcedureSchema


from istsosimport.utils.celery import celery_app
from istsosimport.utils.mail import send_mail
from istsosimport.env import FILE_ERROR_DIRECTORY, db
from istsosimport.db.models import EventTime, Measure, ProcObs, Procedure
from istsosimport.db.utils import get_schema_session


log = logging.getLogger()


# @celery_app.task(bind=True)
def import_data(id_prc, filename, separator, config, csv_mapping, service):
    with ExitStack() as stack:
        session = stack.enter_context(get_schema_session(service))
        procedure = (
            session.query(Procedure)
            .options(
                joinedload(Procedure.proc_obs).joinedload(ProcObs.observed_property)
            )
            .get(id_prc)
        )
        file_eror_name = FILE_ERROR_DIRECTORY / str(
            procedure.name_prc + "_" + str(datetime.now())
        )
        procedure_dict = ProcedureSchema().dump(procedure)

        file_error = open(file_eror_name, "w")
        with open(os.path.join(config["UPLOAD_FOLDER"], filename)) as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=separator)
            csv_writer = csv.DictWriter(
                file_error, delimiter=separator, fieldnames=csvreader.fieldnames
            )
            total_succeed = 0
            total_rows = 0
            error_message = []
            for row in csvreader:
                total_rows = total_rows + 1
                date_col = csv_mapping[
                    "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"
                ]
                eventtime = EventTime(
                    id_prc_fk=procedure_dict["id_prc"],
                    time_eti=isodate.parse_datetime(row[date_col]),
                )
                for proc in procedure_dict["proc_obs"]:
                    val_col = csv_mapping[proc["observed_property"]["def_opr"]]
                    try:
                        floated_value = float(row[val_col])
                    except Exception as e:
                        error_message.append(e)
                        csv_writer.writerow(row)
                        continue
                    measure = Measure(val_msr=floated_value, id_pro_fk=proc["id_pro"])
                    measure.set_quality(proc)
                    eventtime.measures.append(measure)
                    session.add(eventtime)
                try:
                    session.commit()
                    total_succeed = total_succeed + 1
                except exc.SQLAlchemyError as e:
                    log.error(e)
                    error_message.append(e)
                    csv_writer.writerow(row)
                    db.session.rollback()
                    stack.pop_all().close()
                    session = stack.enter_context(get_schema_session(service))

        file_error.close()
        template = render_template(
            "mail_template.html",
            procedure=procedure_dict,
            number_imported=total_succeed,
            total_row=total_rows,
            error_message=error_message,
            file_error=file_eror_name,
        )
    print(template)
    send_mail("theo.lechemia@ecrins-parcnational.fr", "recap", template)
