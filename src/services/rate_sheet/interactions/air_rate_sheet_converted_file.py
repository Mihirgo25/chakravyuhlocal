import os, csv
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from micro_services.client import *

from services.rate_sheet.interactions.upload_file import upload_media_file
from services.rate_sheet.interactions.validate_air_freight_object import (
    validate_air_freight_object,
)
from fastapi.encoders import jsonable_encoder
from services.rate_sheet.helpers import *
import chardet
from services.rate_sheet.interactions.fcl_rate_sheet_converted_file import (
    set_processed_percent,
    valid_hash,
)
from micro_services.client import maps


def get_airport_id(port_code, country_code):
    input = {"filters": {"type": "airport", "port_code": port_code, "status": "active"}}
    locations_data = maps.list_locations(input)
    if "list" in locations_data and len(locations_data["list"]) > 0:
        airport_ids = locations_data["list"][0]["id"]
    else:
        airport_ids = None
    return airport_ids


def get_airline_id(airline_name):
    airline_name = airline_name.lower()
    try:
        airline_id = maps.list_operators(
            {"filters": {"q": airline_name, "operator_type": "airline"}}
        )["list"][0]["id"]
    except:
        airline_id = None
    return airline_id


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
            blank_field = []
            is_main_rate_row = False
            if row["origin_airport"]:
                is_main_rate_row = True

            if valid_hash(row, present_field, blank_field):
                if rows:
                    last_row = list(row.values())
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

            elif valid_hash(
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
                    "validity_start",
                    "validity_end",
                    "packing_type",
                    "handling_type",
                    "price_type",
                    "density_category",
                    "density_ratio",
                ],
            ):
                rows.append(row)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
            else:
                list_opt = []
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
        create_air_freight_rate_delays,
    )

    keys_to_extract = [
        "commodity",
        "operation_type",
        "min_price",
        "currency",
        "validity_start",
        "validity_end",
        "commodity_type",
        "commodity_sub_type",
        "packing_type",
        "handling_type",
        "price_type",
        "density_category",
        "density_ratio",
    ]
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    object["commodity"] = object["commodity"].lower().strip()
    object["commodity_type"] = object["commodity_type"].lower().strip()
    object["commodity_sub_type"] = object["commodity_sub_type"].lower().strip()
    object["currency"] = object["currency"].upper().strip()
    object["price_type"] = object["price_type"].lower().strip()
    object["density_category"] = object["density_category"].lower().strip()
    object["density_ratio"] = "1:{}".format(object["density_ratio"].strip())

    object["validity_start"] = convert_date_format(object.get("validity_start"))
    object["validity_end"] = convert_date_format(object.get("validity_end"))

    object["length"] = 300
    object["breadth"] = 300
    object["height"] = 300

    object["rate_type"] = "general"
    object["initial_volume"] = None
    object["available_volume"] = None
    object["initial_gross_weight"] = None
    object["available_gross_weight"] = None
    object["weight_slabs"] = []

    object["origin_airport_id"] = get_airport_id(
        rows[0]["origin_airport"].upper().strip(),
        rows[0]["origin_country"].upper().strip(),
    )
    object["destination_airport_id"] = get_airport_id(
        rows[0]["destination_airport"].upper().strip(),
        rows[0]["destination_country"].upper().strip(),
    )
    object["airline_id"] = get_airline_id(rows[0]["airline"].strip())
    object["shipment_type"] = object["packing_type"]
    object["weight_slabs"] = []

    for slab in rows:
        weight_slab = {}
        weight_slab["lower_limit"] = slab["lower_limit"].strip()
        weight_slab["upper_limit"] = slab["upper_limit"].strip()
        weight_slab["tariff_price"] = slab["tariff_price"].strip()
        weight_slab["currency"] = object["currency"]
        weight_slab["unit"] = object.get("unit")
        object["weight_slabs"].append(weight_slab)

    object["service_provider_id"] = params.get("service_provider_id")
    object["performed_by_id"] = params.get("performed_by_id")
    object["source"] = "rate_sheet"

    operation_types = object["operation_type"].lower().split(",")
    packing_types = object["packing_type"].lower().split(",")
    handling_types = object["handling_type"].lower().split(",")

    for operation in operation_types:
        object["operation_type"] = operation
        for packing in packing_types:
            object["shipment_type"] = packing
            for handling in handling_types:
                object["stacking_type"] = handling
                object["rate_sheet_id"] = params["id"]
                request_params = object
                validation = write_air_freight_freight_object(
                    request_params, csv_writer, params, converted_file, last_row
                )
                if validation.get("valid"):
                    object["rate_sheet_validation"] = True
                    create_air_freight_rate_delays.apply_async(
                        kwargs={"request": object}, queue="low"
                    )
                else:
                    print(validation.get("error"))


def write_air_freight_freight_object(rows, csv, params, converted_file, last_row):
    object_validity = validate_air_freight_object(converted_file.get("module"), rows)
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


def process_air_freight_local(params, converted_file, update):
    valid_headers = [
        "airport",
        "country",
        "airline",
        "trade_type",
        "commodity",
        "commodity_type",
        "code",
        "unit",
        "min_price",
        "base_price",
        "currency",
        "lower_limit",
        "upper_limit",
        "price",
        "remark1",
        "remark2",
        "remark3",
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
                "airport",
                "country",
                "airline",
                "trade_type",
                "commodity",
                "commodity_type",
                "code",
                "unit",
                "min_price",
                "base_price",
                "currency",
            ]
            blank_field = []
            is_main_rate_row = False
            if row["airport"]:
                is_main_rate_row = True

            if valid_hash(row, present_field, blank_field):
                if rows:
                    last_row = list(row.values())
                    # Create previous rate if previous rate was valid
                    if is_previous_rate_valid:
                        create_air_freight_local_rate(
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

            elif rows and (
                valid_hash(
                    row,
                    ["lower_limit", "upper_limit", "tariff_price"],
                    [
                        "airport",
                        "country",
                        "airline",
                        "trade_type",
                        "commodity",
                        "commodity_type",
                        "code",
                        "unit",
                        "min_price",
                        "base_price",
                        "currency",
                    ],
                )
                or valid_hash(
                    row,
                    ["code", "unit", "min_price", "base_price", "currency"],
                    [
                        "airport",
                        "country",
                        "airline",
                        "trade_type",
                        "commodity",
                        "commodity_type",
                        "lower_limit",
                        "upper_limit",
                        "price",
                    ],
                )
            ):
                rows.append(row)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
            else:
                list_opt = []
                if rows and is_previous_rate_valid and is_main_rate_row:
                    last_row = list(row.values())
                    create_air_freight_local_rate(
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
        create_air_freight_local_rate(
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


def write_air_freight_local_object(rows, csv, params, converted_file, last_row):
    object_validity = validate_air_freight_object(converted_file.get("module"), rows)
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


def create_air_freight_local_rate(
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
        create_air_freight_rate_local_delay,
    )

    keys_to_extract = [
        "trade_type",
        "commodity",
        "commodity_type",
        "airport",
        "airline",
    ]
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    object["airport_id"] = get_airport_id(
        rows[0]["airport"].upper().strip(), rows[0]["country"].upper().strip()
    )
    object["airline_id"] = get_airline_id(rows[0]["airline"].strip())
    object["trade_type"] = object["trade_type"].lower().strip()
    object["commodity"] = object["commodity"].lower().strip()
    object["commodity_type"] = object["commodity_type"].lower().strip()

    object["service_provider_id"] = params.get("service_provider_id")
    object["performed_by_id"] = params.get("performed_by_id")
    object["line_items"] = []
    object["rate_type"] = "general"
    for slab in rows:
        if slab.get("code"):
            keys_to_extract = ["code", "unit", "min_price", "currency"]
            line_item = dict(
                filter(lambda item: item[0] in keys_to_extract, slab.items())
            )
            line_item["currency"] = line_item["currency"].upper().strip()
            line_item["unit"] = line_item["unit"].lower().strip()
            line_item["code"] = line_item["code"].upper().strip()
            line_item["price"] = slab["base_price"]
            remarks = [slab["remark1"], slab["remark2"], slab["remark3"]]
            line_item["remark"] = list(filter(lambda x: x is not None, remarks))
            line_item["slabs"] = []
            object["line_items"].append(line_item)
        else:
            keys_to_extract = ["lower_limit", "upper_limit", "price"]
            weight_slab = dict(
                filter(lambda item: item[0] in keys_to_extract, slab.items())
            )
            object["line_items"][-1]["slabs"].append(weight_slab)
    for line_item in object["line_items"]:
        if not line_item.get("slabs"):
            continue
        for slab in line_item("slabs"):
            slab["currency"] = line_item["currency"]

    request_params = object
    validation = write_air_freight_local_object(
        request_params, csv_writer, params, converted_file, last_row
    )
    if validation.get("valid"):
        object["rate_sheet_validation"] = True
        object["rate_sheet_id"] = params["rate_sheet_id"]
        create_air_freight_rate_local_delay.apply_async(kwargs={"request": object}, queue="low")
    else:
        print(validation.get("error"))


def process_air_freight_surcharge(params, converted_file, update):
    valid_headers = [
        "origin_airport",
        "origin_country",
        "destination_airport",
        "destination_country",
        "airline",
        "operation_type",
        "commodity",
        "commodity_type",
        "code",
        "unit",
        "price",
        "min_price",
        "currency",
        "remark1",
        "remark2",
        "remark3",
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
                "airline",
                "operation_type",
                "commodity",
                "commodity_type",
                "code",
                "unit",
                "price",
                "min_price",
                "currency",
            ]
            blank_field = []
            is_main_rate_row = False
            if row["origin_airport"]:
                is_main_rate_row = True

            if valid_hash(row, present_field, blank_field):
                if rows:
                    last_row = list(row.values())
                    # Create previous rate if previous rate was valid
                    if is_previous_rate_valid:
                        create_air_freight_surcharge_rate(
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

            elif rows and (
                valid_hash(
                    row,
                    ["code", "unit", "price", "min_price", "currency"],
                    [
                        "origin_airport",
                        "origin_country",
                        "destination_airport",
                        "destination_country",
                        "airline",
                        "operation_type",
                        "commodity",
                        "commodity_type",
                    ],
                )
            ):
                rows.append(row)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
            else:
                list_opt = []
                if rows and is_previous_rate_valid and is_main_rate_row:
                    last_row = list(row.values())
                    create_air_freight_surcharge_rate(
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
        create_air_freight_surcharge_rate(
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


def write_air_freight_surcharge_object(rows, csv, params, converted_file, last_row):
    object_validity = validate_air_freight_object(converted_file.get("module"), rows)
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


def create_air_freight_surcharge_rate(
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
        create_air_freight_rate_surcharge_delay,
    )

    keys_to_extract = ["commodity", "commodity_type", "operation_type"]
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))

    object["origin_airport_id"] = get_airport_id(
        rows[0]["origin_airport"].upper().strip(),
        rows[0]["origin_country"].upper().strip(),
    )
    object["destination_airport_id"] = get_airport_id(
        rows[0]["destination_airport"].upper().strip(),
        rows[0]["destination_country"].upper().strip(),
    )
    object["airline_id"] = get_airline_id(rows[0]["airline"].strip())
    object["commodity"] = object["commodity"].lower().strip()
    object["commodity_type"] = object["commodity_type"].lower().strip()
    object["operation_type"] = object["operation_type"].lower().strip()

    object["line_items"] = []
    for slab in rows:
        keys_to_extract = ["code", "unit", "price", "min_price", "currency"]
        line_item = dict(filter(lambda item: item[0] in keys_to_extract, slab.items()))
        line_item["currency"] = line_item["currency"].upper().strip()
        line_item["unit"] = line_item["unit"].upper().strip()
        line_item["code"] = line_item["code"].upper().strip()
        remarks = [slab["remark1"], slab["remark2"], slab["remark3"]]
        line_item["remark"] = list(filter(lambda x: x is not None, remarks))
        object["line_items"].append(line_item)

    operation_types = object["operation_type"].split(",")
    object["service_provider_id"] = params.get("service_provider_id")
    object["rate_sheet_id"] = params["rate_sheet_id"]
    for operation in operation_types:
        object["operation_type"] = operation
        request_params = object
        validation = write_air_freight_local_object(
            request_params, csv_writer, params, converted_file, last_row
        )
        if validation.get("valid"):
            object["rate_sheet_validation"] = True
            create_air_freight_rate_surcharge_delay.apply_async(
                kwargs={"request": object}, queue="low"
            )
        else:
            print(validation.get("error"))
