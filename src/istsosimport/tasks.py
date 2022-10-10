from contextlib import ExitStack
import csv
from datetime import date, datetime
import os
import json
import logging

import pandas as pd
import requests as req
import isodate

from flask import render_template
from sqlalchemy import exc, update
from istsosimport.schemas import ProcedureSchema


from istsosimport.utils.celery import celery_app
from istsosimport.utils.mail import send_mail
from istsosimport.env import FILE_ERROR_DIRECTORY, db
from istsosimport.db.models import EventTime, Import, Measure, ProcObs, Procedure
from istsosimport.db.utils import get_schema_session


log = logging.getLogger()


@celery_app.task(bind=True)
def import_data(self, import_dict, filename, separator, config, csv_mapping, service):
    procedure_dict = import_dict["procedure"]
    file_eror_name = str(procedure_dict["name_prc"] + "_" + str(datetime.now()))

    file_error = open(str(FILE_ERROR_DIRECTORY / file_eror_name), "w")
    with open(os.path.join(config["UPLOAD_FOLDER"], filename)) as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=separator)
        csv_writer = csv.DictWriter(
            file_error, delimiter=separator, fieldnames=csvreader.fieldnames
        )
        total_succeed = 0
        total_rows = 0
        error_message = []
        for row in csvreader:
            with get_schema_session(service) as current_session:
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
                    current_session.add(eventtime)
                try:
                    current_session.commit()
                    db.session.commit()
                    total_succeed = total_succeed + 1
                except exc.SQLAlchemyError as e:
                    log.error(e)
                    error_message.append(e)
                    csv_writer.writerow(row)

        file_error.close()
        template = render_template(
            "mail_template.html",
            procedure=procedure_dict,
            number_imported=total_succeed,
            total_row=total_rows,
            error_message=error_message,
            file_error=str(FILE_ERROR_DIRECTORY / file_eror_name),
        )
    with get_schema_session(service) as session:
        session.execute(
            update(Import)
            .where(Import.id_import == import_dict["id_import"])
            .values(
                nb_row_total=total_rows,
                nb_row_inserted=total_succeed,
                error_file=file_eror_name,
            )
        )
        session.commit()

    send_mail(import_dict["email"], "Import IstSOS", template)
