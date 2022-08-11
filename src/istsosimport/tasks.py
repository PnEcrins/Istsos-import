import csv
import os
import json
import logging

import pandas as pd
import requests as req

from flask import render_template, current_app

from istsosimport.utils.celery import celery_app
from istsosimport.utils.mail import send_mail
from istsosimport.env import FILE_ERROR_DIRECTORY

log = logging.getLogger()


@celery_app.task(bind=True)
def run_insert_observation_api(
    self,
    filename,
    in_ordered_columns,
    out_ordered_columns,
    csv_mapping,
    last_obs,
    procedure,
    config,
    recipient,
    separator,
    base_url,
):
    # create a csv for error data
    filename_error = "error_" + filename
    csv_in_error_path = os.path.join(FILE_ERROR_DIRECTORY, filename_error)
    data_in_error_file = open(csv_in_error_path, "w")
    csv_writer = csv.writer(data_in_error_file, delimiter=separator)
    csv_writer.writerow(in_ordered_columns)
    error_message = []
    number_imported = 0
    total_row = 0
    # read the csv in little chunk
    # TODO: parametrize offset_line
    offset_line = 10
    for df in pd.read_csv(
        os.path.join(config["UPLOAD_FOLDER"], filename),
        chunksize=offset_line,
        sep=separator,
    ):
        total_row = total_row + offset_line
        columns = df.columns
        for col in out_ordered_columns:
            # if the column is a quality index and its not in the file
            # add a column to dataframe
            if col.split(":")[-1] == "qualityIndex" and col not in columns:
                # TODO : parametrize it
                df[col] = 100
        # reorder the df in correct order
        df = df[[*in_ordered_columns]]
        date_columns = csv_mapping["urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"]
        start_date = df.min()[date_columns]
        end_date = df.max()[date_columns]
        observations = df.values.tolist()
        new_obs = last_obs
        # attach data to object
        new_obs["result"]["DataArray"]["values"] = observations
        new_obs["samplingTime"]["beginPosition"] = start_date
        new_obs["samplingTime"]["endPosition"] = end_date
        new_obs["result"]["DataArray"]["elementCount"] = str(offset_line)
        new_obs["result"]["DataArray"]["values"] = observations
        log.info(f"Start import data from {start_date} to {end_date}")
        data = json.dumps(
            {
                # TODO parametrize force insert
                "ForceInsert": "false",
                "AssignedSensorId": procedure["assignedid_prc"],
                "Observation": new_obs,
            }
        )
        res = req.post(
            f"{config['ISTSOS_API_URL']}/wa/istsos/services/{config['SERVICE']}/operations/insertobservation",
            data=data,
            auth=None,
            verify=False,
        )
        res_data = res.json()
        if res_data["success"] is True:
            number_imported = number_imported + offset_line
            log.info("Successfully import data from {start_date} to {end_date}")
        else:
            log.error(f"Fail import data from {start_date} to {end_date}")
            error_message.append(res_data["message"])
            csv_writer.writerows(observations)

    data_in_error_file.close()

    email_html = render_template(
        "mail_template.html",
        number_imported=number_imported,
        total_row=total_row,
        error_message=error_message,
        procedure=procedure,
        file_error=filename_error,
        base_url=base_url,
    )
    send_mail(recipient, f"Import report for {procedure['name_prc']}", email_html)
