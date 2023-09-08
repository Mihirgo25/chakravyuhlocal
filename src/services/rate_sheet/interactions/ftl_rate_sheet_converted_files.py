import os, csv
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from micro_services.client import *
from services.rate_sheet.interactions.upload_file import upload_media_file
from services.rate_sheet.interactions.validate_ftl_freight_object import (
    validate_ftl_freight_object,
)
from libs.json_encoder import json_encoder
from services.rate_sheet.helpers import *
import chardet
from libs.parse_numeric import parse_numeric

def process_ftl_freight_freight(params, converted_file, update):
    valid_headers = ['origin_location', 'destination_location', 'truck_type', 'commodity', 'code', 'unit', 'price',
                'currency', 'truck_body_type', 'validity_start', 'validity_end', 'transit_time', 'detention_free_time',
                  'trip_type', 'remark1', 'remark2', 'remark3']
    total_lines = 0
    original_path = get_original_file_path(converted_file)
    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudit.get(
        (RateSheetAudit.object_id == params["rate_sheet_id"])
        & (RateSheetAudit.action_name == "update")
    )
    rate_sheet = json_encoder(rate_sheet)["__data__"]
    created_by_id = rate_sheet["performed_by_id"]
    procured_by_id = rate_sheet["procured_by_id"]
    sourced_by_id = rate_sheet["sourced_by_id"]

    index = -1
    file_path = original_path
    edit_file = open(get_file_path(converted_file), "w")
    last_row = []
    invalidated = False
    with open(file_path, "rb") as f:
        result = chardet.detect(f.read())
        encoding = result["encoding"]

    with open(original_path, mode="rt", encoding=encoding) as file:
        # Read converted file for porcessing
        csv_writer = csv.writer(edit_file)
        input_file = csv.DictReader(file)
        headers = input_file.fieldnames
        if len(set(valid_headers) & set(headers)) != len(valid_headers):
            error_file = ["invalid header"]
            csv_writer.writerow(error_file)
            invalidated = True

        for row in input_file:
            total_lines += 1
        set_total_line(converted_file, total_lines)
        set_processed_percent(0, converted_file)
        csv_writer.writerow(headers)
        file.seek(0)
        next(file)
        is_previous_rate_valid = True
        for row in input_file:
            if invalidated:
                break
            index += 1
            if not ''.join([str(value) for value in row.values() if value is not None]).strip():
                continue
            for k, v in row.items():
                if v == "":
                    row[k] = None
            
            is_main_rate_row = False
            if row["origin_location"]:
                is_main_rate_row = True
            if valid_hash(row, ["origin_location", "destination_location","truck_type", "code", "unit", "price", "currency", "truck_body_type", "validity_start", "validity_end", "transit_time", "detention_free_time", "trip_type"], ["lower_limit", "upper_limit"]):
                if rows:
                    last_row = list(row.values())
                    if is_previous_rate_valid:
                        create_ftl_freight_freight_rate(
                            params,
                            converted_file,
                            rows,
                            created_by_id,
                            procured_by_id,
                            sourced_by_id,
                            csv_writer,
                            last_row,
                        )
                    else:
                        is_previous_rate_valid = True
                    
                    set_current_processing_line(index - 1, converted_file)
                    percent = (
                        get_current_processing_line(converted_file) / total_lines
                    ) * 100
                    set_processed_percent(percent, params)
                else:
                    list_opt = list(row.values())
                    csv_writer.writerow(list_opt)
                rows = [row]
            elif valid_hash(row, ["code", "unit", "price", "currency"], ["origin_location", "destination_location", "truck_type", "truck_body_type", "commodity", "validity_start", "validity_end", "transit_time", "detention_free_time", "trip_type"]):
                rows.append(row)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
            else:
                list_opt = []
                if rows and is_previous_rate_valid and is_main_rate_row:
                    last_row = list(row.values())
                    create_ftl_freight_freight_rate(
                        params,
                        converted_file,
                        rows,
                        created_by_id,
                        procured_by_id,
                        sourced_by_id,
                        csv_writer,
                        last_row,
                    )
                    set_current_processing_line(index - 1, converted_file)
                    percent = (
                        get_current_processing_line(converted_file) / total_lines
                    ) * 100
                    set_processed_percent(percent, params)
                else:
                    list_opt = list(row.values())
                list_opt.append("Invalid Row")
                csv_writer.writerow(list_opt)
                if is_previous_rate_valid:
                    converted_file["rates_count"] += 1
                is_previous_rate_valid = False
                rows = []
    if rows and is_previous_rate_valid and not invalidated:
        create_ftl_freight_freight_rate(
            params,
            converted_file,
            rows,
            created_by_id,
            procured_by_id,
            sourced_by_id,
            csv_writer,
            "",
        )
    set_current_processing_line(total_lines, converted_file)
    try:
        valid = converted_file.get("valid_rates_count")
        total = converted_file.get("rates_count")
        percent_completed = (valid / total) * 100
    except:
        valid = 0
        total = 0
        percent_completed = 0
    percent = (get_current_processing_line(converted_file) / total_lines) * 100
    converted_file["percent"] = percent_completed
    edit_file.flush()
    converted_file["file_url"] = upload_media_file(get_file_path(converted_file))
    edit_file.close()
    if valid == total and total != 0:
        update.status = "complete"
        converted_file["status"] = "complete"
    elif valid == 0:
        update.status = "uploaded"
        converted_file["status"] = "invalidated"
    else:
        update.status = "partially_complete"
        converted_file["status"] = "partially_complete"

    set_processed_percent(percent_completed, params)
    try:
        os.remove(get_original_file_path(converted_file))
        os.remove(get_file_path(converted_file))
    except:
        return


def create_ftl_freight_freight_rate(
    params,
    converted_file,
    rows,
    created_by_id,
    procured_by_id,
    sourced_by_id,
    csv_writer,
    last_row,
):
    from services.ftl_freight_rate.ftl_celery_worker import create_ftl_freight_rate_delay
    keys_to_extract =  ["origin_location", "destination_location", "commodity", "transit_time", "detention_free_time", "validity_start", "validity_end", "trip_type", "truck_type", "truck_body_type"]
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))

    object["origin_location_id"] = get_location_id(rows[0]['origin_location'])
    object["destination_location_id"] = get_location_id(rows[0]['destination_location'])

    object["line_items"] = []

    for data in rows:
        keys_to_extract = ['code', 'unit', 'price', 'currency']
        line_item = dict(filter(lambda item: item[0] in keys_to_extract, data.items()))
        line_item['remarks'] = list(set([data["remark1"], data["remark2"], data["remark3"]]))
        object['line_items'].append(line_item)

    validity_start = ''.join([val for val in object['validity_start'] if val.isdigit()])
    validity_end = ''.join([val for val in object['validity_end'] if val.isdigit()])
    object['validity_end'] = datetime.strptime(validity_end, '%d%m%Y')
    object['validity_start'] = datetime.strptime(validity_start, '%d%m%Y')
    object["rate_sheet_id"] = params["id"]
    object["performed_by_id"] = created_by_id
    object["service_provider_id"] = params.get("service_provider_id")
    object["procured_by_id"] = procured_by_id
    object["sourced_by_id"] = sourced_by_id

    request_params = object
    validation = write_ftl_freight_freight_object(
        request_params, csv_writer, params, converted_file, last_row
    )
    if validation.get("valid"):
        object["rate_sheet_validation"] = True
        create_ftl_freight_rate_delay.apply_async(
            kwargs={"request": object}, queue="low"
        )
    else:
        print(validation.get("error"))


def write_ftl_freight_freight_object(rows, csv, params, converted_file, last_row):
    object_validity = validate_ftl_freight_object(converted_file.get("module"), rows)
    if object_validity["valid"]:
        csv.writerow(last_row)
        converted_file["valid_rates_count"] = (
            int(converted_file["valid_rates_count"]) + 1
        )
    else:
        try:
            error = ["".join(str(object_validity.get("error")))]
            list_opt = error
            csv.writerow(list_opt)
            csv.writerow([])
            csv.writerow(last_row)
        except:
            print("no csv")
    converted_file["rates_count"] = int(converted_file["rates_count"]) + 1
    return object_validity

