import os, csv, json, math
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from micro_services.client import *

from services.rate_sheet.interactions.upload_file import upload_media_file
from services.rate_sheet.interactions.validate_air_freight_object import (
    validate_air_freight_object,
)
from database.db_session import rd

from fastapi.encoders import jsonable_encoder

from datetime import datetime
import dateutil.parser as parser
from database.rails_db import get_shipping_line, get_organization
from services.rate_sheet.helpers import *
import chardet
from libs.parse_numeric import parse_numeric
from services.rate_sheet.interactions.fcl_rate_sheet_converted_file import (
    set_processed_percent,
    valid_hash,
)

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))


def process_air_freight_freight(params, converted_file, update):
    valid_headers = [
        "origin_airport",
        "origin_country",
        "destination_airport",
        "destination_country",
        "commodity",
        "commodity_type",
        "commodity_sub_type",
        "airline",
        "operation_type",
        "min_price",
        "currency",
        "lower_limit",
        "upper_limit",
        "tariff_price",
        "validity_start",
        "validity_end",
        "packing_type",
        "handling_type",
        "price_type",
        "density_category",
        "density_ratio",
    ]
    total_lines = 0
    original_path = get_original_file_path(converted_file)
    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudit.get(
        (RateSheetAudit.object_id == params["rate_sheet_id"])
        & (RateSheetAudit.action_name == "update")
    )
    rate_sheet = jsonable_encoder(rate_sheet)["__data__"]
    created_by_id = rate_sheet["performed_by_id"]
    procured_by_id = rate_sheet["procured_by_id"]
    sourced_by_id = rate_sheet["sourced_by_id"]
    index = -1 if index < 0 else index
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

        if len(set(valid_headers) & set(headers)) != len(headers):
            error_file = ["invalid header"]
            csv_writer.writerow(error_file)
            invalidated = True

        for row in input_file:
            total_lines += 1
        # Set Initial Rate Sheets count
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
            if not "".join(list(row.values())).strip():
                continue
            for k, v in row.items():
                if v == "":
                    row[k] = None
            present_field = [
                "origin_airport",
                "origin_country",
                "destination_airport",
                "destination_country",
                "commodity",
                "commodity_type",
                "commodity_sub_type",
                "airline",
                "operation_type",
                "min_price",
                "currency",
                "lower_limit",
                "upper_limit",
                "tariff_price",
                "validity_start",
                "validity_end",
                "packing_type",
                "handling_type",
                "price_type",
                "density_category",
                "density_ratio",
            ]
            blank_field = None
            is_main_rate_row = False
            if row["origin_port"]:
                is_main_rate_row = True

            if valid_hash(row, present_field, blank_field):
                if rows:
                    last_row = list(row.values())
                    print(is_previous_rate_valid, "1", params)
                    # Create previous rate if previous rate was valid
                    if is_previous_rate_valid:
                        create_air_freight_freight_rate(
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
                    # Set Processing percent
                    set_current_processing_line(index - 1, converted_file)
                    percent = (
                        get_current_processing_line(converted_file) / total_lines
                    ) * 100
                    set_processed_percent(percent, params)
                else:
                    list_opt = list(row.values())
                    csv_writer.writerow(list_opt)
                rows = [row]
            elif (
                valid_hash(
                    row,
                    ["lower_limit", "upper_limit", "tariff_price"],
                    [
                        "origin_airport",
                        "origin_country",
                        "destination_airport",
                        "destination_country",
                        "commodity",
                        "commodity_type",
                        "commodity_sub_type",
                        "airline",
                        "operation_type",
                        "min_price",
                        "currency",
                        "weight_lower_limit",
                        "weight_upper_limit",
                        "weight_limit_price",
                        "weight_limit_currency",
                        "destination_detention_free_limit",
                        "destination_detention_lower_limit",
                        "destination_detention_upper_limit",
                        "destination_detention_price",
                        "destination_detention_currency",
                        "schedule_type",
                        "payment_term",
                        "rate_type",
                    ],
                )
                or valid_hash(
                    row,
                    ["weight_free_limit"],
                    [
                        "origin_port",
                        "origin_main_port",
                        "destination_port",
                        "destination_main_port",
                        "container_size",
                        "container_type",
                        "commodity",
                        "shipping_line",
                        "code",
                        "unit",
                        "price",
                        "currency",
                        "validity_start",
                        "validity_end",
                        "weight_lower_limit",
                        "weight_upper_limit",
                        "weight_limit_price",
                        "weight_limit_currency",
                        "destination_detention_free_limit",
                        "destination_detention_lower_limit",
                        "destination_detention_upper_limit",
                        "destination_detention_price",
                        "destination_detention_currency",
                        "schedule_type",
                        "payment_term",
                        "rate_type",
                    ],
                )
                or valid_hash(
                    row,
                    [
                        "weight_free_limit",
                        "weight_lower_limit",
                        "weight_upper_limit",
                        "weight_limit_price",
                        "weight_limit_currency",
                    ],
                    [
                        "origin_port",
                        "origin_main_port",
                        "destination_port",
                        "destination_main_port",
                        "container_size",
                        "container_type",
                        "commodity",
                        "shipping_line",
                        "code",
                        "unit",
                        "price",
                        "currency",
                        "validity_start",
                        "validity_end",
                        "destination_detention_free_limit",
                        "destination_detention_lower_limit",
                        "destination_detention_upper_limit",
                        "destination_detention_price",
                        "destination_detention_currency",
                        "schedule_type",
                        "payment_term",
                        "rate_type",
                    ],
                )
                or valid_hash(
                    row,
                    [
                        "weight_lower_limit",
                        "weight_upper_limit",
                        "weight_limit_price",
                        "weight_limit_currency",
                    ],
                    [
                        "origin_port",
                        "origin_main_port",
                        "destination_port",
                        "destination_main_port",
                        "container_size",
                        "container_type",
                        "commodity",
                        "shipping_line",
                        "code",
                        "unit",
                        "price",
                        "currency",
                        "validity_start",
                        "validity_end",
                        "weight_free_limit",
                        "destination_detention_free_limit",
                        "destination_detention_lower_limit",
                        "destination_detention_upper_limit",
                        "destination_detention_price",
                        "destination_detention_currency",
                        "schedule_type",
                        "payment_term",
                        "rate_type",
                    ],
                )
                or valid_hash(
                    row,
                    ["destination_detention_free_limit"],
                    [
                        "origin_port",
                        "origin_main_port",
                        "destination_port",
                        "destination_main_port",
                        "container_size",
                        "container_type",
                        "commodity",
                        "shipping_line",
                        "code",
                        "unit",
                        "price",
                        "currency",
                        "validity_start",
                        "validity_end",
                        "weight_free_limit",
                        "weight_lower_limit",
                        "weight_upper_limit",
                        "weight_limit_price",
                        "weight_limit_currency",
                        "destination_detention_lower_limit",
                        "destination_detention_upper_limit",
                        "destination_detention_price",
                        "destination_detention_currency",
                        "schedule_type",
                        "payment_term",
                        "rate_type",
                    ],
                )
                or valid_hash(
                    row,
                    [
                        "destination_detention_free_limit",
                        "destination_detention_lower_limit",
                        "destination_detention_upper_limit",
                        "destination_detention_price",
                        "destination_detention_currency",
                    ],
                    [
                        "origin_port",
                        "origin_main_port",
                        "destination_port",
                        "destination_main_port",
                        "container_size",
                        "container_type",
                        "commodity",
                        "shipping_line",
                        "code",
                        "unit",
                        "price",
                        "currency",
                        "validity_start",
                        "validity_end",
                        "weight_free_limit",
                        "weight_lower_limit",
                        "weight_upper_limit",
                        "weight_limit_price",
                        "weight_limit_currency",
                        "schedule_type",
                        "payment_term",
                        "rate_type",
                    ],
                )
                or valid_hash(
                    row,
                    [
                        "destination_detention_lower_limit",
                        "destination_detention_upper_limit",
                        "destination_detention_price",
                        "destination_detention_currency",
                    ],
                    [
                        "origin_port",
                        "origin_main_port",
                        "destination_port",
                        "destination_main_port",
                        "container_size",
                        "container_type",
                        "commodity",
                        "shipping_line",
                        "code",
                        "unit",
                        "price",
                        "currency",
                        "validity_start",
                        "validity_end",
                        "weight_free_limit",
                        "weight_lower_limit",
                        "weight_upper_limit",
                        "weight_limit_price",
                        "weight_limit_currency",
                        "destination_detention_free_limit",
                        "schedule_type",
                        "payment_term",
                        "rate_type",
                    ],
                )
            ):
                rows.append(row)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
            else:
                list_opt = []
                print(is_previous_rate_valid, "2", params)
                if rows and is_previous_rate_valid and is_main_rate_row:
                    last_row = list(row.values())
                    create_air_freight_freight_rate(
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
        create_air_freight_freight_rate(
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

    print(update.status, converted_file, "3")

    set_processed_percent(percent_completed, params)
    try:
        os.remove(get_original_file_path(converted_file))
        os.remove(get_file_path(converted_file))
    except:
        return


def create_air_freight_freight_rate(
    params,
    converted_file,
    rows,
    created_by_id,
    procured_by_id,
    sourced_by_id,
    csv_writer,
    last_row,
):
    from celery_worker import (
        create_air_freight_rate_delay,
    )
    keys_to_extract = ["origi   n_airport", "origin_country", "destination_airport", "destination_country", "commodity", "commodity_type", "commodity_sub_type", "airline", "operation_type", "min_price", "currency", "validity_start", "validity_end", "packing_type", "handling_type", "price_type", "density_category", "density_ratio"]
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    rows["origin_airport"] = object["origin_airport"].upper().strip()
    rows["origin_country"] = object["origin_country"].upper().strip()
    rows["destination_airport"] = object["destination_airport"].upper().strip()
    rows["destination_country"] = object["destination_country"].upper().strip()
    rows["commodity"] = object["commodity"].lower().strip()
    rows["commodity_type"] = object["commodity_type"].lower().strip()
    rows["commodity_sub_type"] = object["commodity_sub_type"].lower().strip()
    rows["airline"] = object["airline"].strip()
    rows["currency"] = object["currency"].upper().strip()
    rows["price_type"] = object["price_type"].lower().strip()
    rows["density_category"] = object["density_category"].lower().strip()
    rows["density_ratio"] = object["density_ratio"].strip()
    object["density_ratio"] = "1:{}".format(object["density_ratio"].strip())
    object['validity_start'] = convert_date_format(object.get('validity_start'))
    object['validity_end'] = convert_date_format(object.get('validity_end'))
    object["rate_type"] = 'general'
    object["initial_volume"] = None
    object["available_volume"] = None
    object["initial_gross_weight"] = None
    object["available_gross_weight"] = None
    object["weight_slabs"] = []

    for slab in rows:
        weight_slab = {}
        weight_slab["lower_limit"] = slab["lower_limit"].strip()
        weight_slab["upper_limit"] = slab["upper_limit"].strip()
        weight_slab["tariff_price"] = slab["tariff_price"].strip()
        weight_slab["currency"] = object["currency"]
        object["weight_slabs"].append(weight_slab)
    
    object["service_provider_id"] = params.get('service_provider_id')
    object["cogo_entity_id"] = params.get('cogo_entity_id')
    object["source"] = "rate_sheet"

    operation_types = object["operation_type"].lower().split(',')
    packing_types = object["packing_types"].lower().split(',')
    handling_types = object["handling_types"].lower().split(',')

    for operation in operation_types:
        object['operation_type'] = operation
        for packing in packing_types:
            object['packing_type'] = packing
            for handling in handling_types:
                object['handling_type'] = handling
                
    request_params = 0
    validation = write_air_freight_freight_object(
        request_params, csv_writer, params, converted_file, last_row
    )
    if validation.get("valid"):
        object["rate_sheet_validation"] = True
        create_air_freight_rate_delay.apply_async(
            kwargs={"request": object}, queue="air_freight_rate"
        )
    else:
        print(validation.get("error"))


def write_air_freight_freight_object(rows, csv, params, converted_file, last_row):
    object_validity = validate_air_freight_object(converted_file.get('module'), rows)
    if object_validity["valid"]:
        csv.writerow(last_row)
        converted_file['valid_rates_count'] = int(converted_file['valid_rates_count'])+1
    else:
        try:
            error = ["".join(str(object_validity.get("error")))]
            list_opt = error
            csv.writerow(list_opt)
            csv.writerow([])
            csv.writerow(last_row)
        except:
            print('no csv')
    converted_file['rates_count'] = int(converted_file['rates_count'])+1
    return object_validity
