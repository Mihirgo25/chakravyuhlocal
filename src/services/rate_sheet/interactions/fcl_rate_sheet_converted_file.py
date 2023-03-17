import os, csv, json
from csv import writer
import time
import shutil
import urllib.request
from libs.download_csv import download_file
from services.rate_sheet.models.rate_sheet import RateSheets
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudits
import pandas as pd
from rails_client import client
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import (
    create_fcl_freight_rate_data, create_fcl_freight_rate
)
from services.fcl_freight_rate.interaction.extend_create_fcl_freight_rate import (
    extend_create_fcl_freight_rate_data,
)
from database.db_session import rd
import wget
import ssl, time, requests
import services.rate_sheet.interactions.fcl_rate_sheet_converted_file as process_rate_sheet
from fastapi.encoders import jsonable_encoder
from libs.locations import list_locations
from datetime import datetime
import dateutil.parser as parser

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

csv_options = {
    "encoding": "iso-8859-1",
    "quotechar": None,
    "skip_blank_lines": True,
    "skipinitialspace": True,
    "skiprows": lambda x: x.startswith(
        ","
    ),
}

last_line_hash = "last_line"
total_line_hash = "total_line"


def last_line_key(params):
    return f"rate_sheet_converted_file_last_line_{params['id']}"


def set_last_line(last_line, params):
    if rd:
        rd.hset(last_line_hash, last_line_key(params), last_line)


def get_last_line(params):
    if rd:
        try:
            cached_response = rd.hget(last_line_hash, last_line_key(params))
            return int(cached_response)
        except:
            return 0


def delete_last_line(last_line_hash):
    if rd:
        rd.delete(last_line_hash, last_line_key)

def errors_present_key(params):
    return  f"rate_sheet_converted_file_errors_present_#{params['id']}"

def delete_errors_present(params):
    if rd:
        rd.delete(last_line_hash, errors_present_key(params))



def total_line_keys(params):
    return f"rate_sheet_converted_file_total_lines_{params['id']}"


def set_total_line(params, total_line):
    if rd:
        rd.hset(total_line_hash, total_line_keys(params), total_line)


def get_total_line(params):
    if rd:
        cached_response = rd.hget(total_line_hash, total_line_keys(params))
        return cached_response


def delete_total_line(total_line_hash, params):
    if rd:
        rd.delete(total_line_hash, total_line_keys(params))



def mark_processing(params):
    params.status = "processing"
    return params


def reset_counters(params):
    total_lines = get_total_line(params)
    if total_lines == 0:
        delete_temp_data(params)
    set_original_file_path(params)


def delete_temp_data(params):
    delete_original_file_path(params)
    delete_file_path(params)
    delete_errors_present(params)
    delete_last_line(params)
    delete_total_line(params)


def get_original_file_path(params):
    os.makedirs("tmp/rate_sheets", exist_ok=True)
    path = os.path.join("tmp", "rate_sheets", f"{params['id']}_original.csv")
    return path


def delete_original_file_path(params):
    try:
        os.remove(get_file_path(params))
    except FileNotFoundError:
        pass


def set_original_file_path(params):
    os.makedirs('tmp/rate_sheets', exist_ok=True)
    file_path = os.path.join('tmp', 'rate_sheets', f"{params['id']}_original.csv")
    with open(file_path, 'wb') as f:
        response = requests.get(params["file_url"])
        print(params["file_url"], "sabsat")
        f.write(response.content)


def get_file_path(params):
    os.makedirs("tmp/rate_sheets", exist_ok=True)
    return os.path.join("tmp", "rate_sheets", f"{params['id']}_original.csv")


def delete_file_path(params):
    try:
        os.remove(get_file_path(params))
    except FileNotFoundError:
        pass

def valid_hash(hash, present_fields, blank_fields):
    print(hash, "hash")
    for field in present_fields:
        if not hash[field]:
            return False

    for field in blank_fields:
        if hash[field]:
            return False
    return True

def get_port_id(port_code):
    filters =  {"type": "seaport", "port_code": port_code, "status": "active"}
    port_id =  list_locations({'filters': str(filters)})['list'][0]["id"]
    return port_id


def get_airport_id(port_code, country_code):
    airport_id = client.ruby.list_locations(
        {
            "filters": {
                "type": "airport",
                "port_code": port_code,
                "status": "active",
                "country_code": country_code,
            },
            "fields": ["id"],
        }
    )["list"][0]["id"]
    return airport_id


def get_shipping_line_id(shipping_line_name):
    shipping_line_id = client.ruby.list_operators(
        {
            "filters": {
                "operator_type": "shipping_line",
                "short_name": shipping_line_name,
                "status": "active",
            }
        }
    )["list"][0]['id']
    return shipping_line_id


def get_airline_id(params):
    airline_id = client.ruby.list_operators(
        {"filters": {"id": params.origin_location_id}}
    )["list"][0]
    return airline_id


def convert_date_format(date):
    print(date)
    if not date:
        return date
    parsed_date = parser.parse(date)
    return datetime.strptime(str(parsed_date.date()), '%Y-%m-%d')

def process_fcl_freight_freight(params):
    total_lines = 0
    original_path = get_original_file_path(params)
    with open(original_path, encoding='iso-8859-1') as file:
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        headers = next(reader)
        for row in reader:
            total_lines += 1
    set_total_line(params, total_lines)

    last_line = get_last_line(params)
    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudits.get((RateSheetAudits.object_id == params["rate_sheet_id"]) & (RateSheetAudits.action_name == 'create') )
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']
    created_by_id = rate_sheet['performed_by_id']
    procured_by_id = rate_sheet['procured_by_id']
    sourced_by_id = rate_sheet['sourced_by_id']
    index = -1
    file_path = get_original_file_path(params)
    print(file_path)
    with open(file_path, encoding='iso-8859-1') as file:
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        next(reader, None)
        input_file = csv.DictReader(open(file_path))
        for row in input_file:
            index += 1
            row = row
            # if index < last_line:
            #     return
            present_field = ['origin_port', 'destination_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'validity_start', 'validity_end', 'code', 'unit', 'price', 'currency']
            blank_field = ['weight_free_limit','weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency', 'destination_detention_free_limit', 'destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency']
            if valid_hash(row, present_field, blank_field):
                if rows:
                    print(rows,"testing-process")
                    create_fcl_freight_freight_rate(
                        params, rows, created_by_id, procured_by_id, sourced_by_id
                    )
                    set_last_line(index, params)
                    # rate_sheet.set_processed_percent = (
                    #     ((params.file_index * 1.0) / rate_sheet.converted_files.count)
                    #     * ((get_last_line * 1.0) / get_total_line)
                    # ) * 100
                rows = [row]
            elif (
                valid_hash(
                    row,
                    ["code", "unit", "price", "currency"],
                    [
                        "origin_port",
                        "origin_main_port",
                        "destination_port",
                        "destination_main_port",
                        "container_size",
                        "container_type",
                        "commodity",
                        "shipping_line",
                        "validity_start",
                        "validity_end",
                        "weight_free_limit",
                        "weight_lower_limit",
                        "weight_upper_limit",
                        "weight_limit_price",
                        "weight_limit_currency",
                        "destination_detention_free_limit",
                        "destination_detention_lower_limit",
                        "destination_detention_upper_limit",
                        "destination_detention_price",
                        "destination_detention_currency",
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
                    ],
                )
            ):
                print("testing-process2")
                rows.append(row)
    print(len(rows))
    if not rows:
        return
    # create_fcl_freight_freight_rate(params, rows, created_by_id, procured_by_id, sourced_by_id)
    # set_last_line(total_lines)
    # rate_sheet.set_processed_percent = (
    #     ((params.file_index * 1.0) / rate_sheet.converted_files.count)
    #     * ((get_last_line * 1.0) / get_total_line)
    # ) * 100



def create_fcl_freight_freight_rate(
    params, rows, created_by_id, procured_by_id, sourced_by_id
):
    keys_to_extract = ['container_size', 'container_type', 'commodity', 'validity_start', 'validity_end', 'schedule_type', 'payment_term']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))

    object['validity_start'] = convert_date_format(object['validity_start'])
    object['validity_end'] = convert_date_format(object['validity_end'])
    for port in [
        "origin_port",
        "origin_main_port",
        "destination_port",
        "destination_main_port",
    ]:
        object[f"{str(port)}_id"] = get_port_id(rows[0][port])

    object["shipping_line_id"] = get_shipping_line_id(rows[0]["shipping_line"])
    object["line_items"] = []
    # incomplete rows
    for t in rows:
        print(t, "sal")
        if t['code']:
            line_item = {
            'code': t['code'],
            'unit': t['unit'],
            'price': t['price'],
            'currency': t['currency'],
            'remarks': [t['remark1'], t['remark2'], t['remark3']] if any([t['remark1'], t['remark2'], t['remark3']]) else None,
            'slabs': []
            }
            object["line_items"].append(line_item)
        elif t['weight_free_limit'] or t['weight_lower_limit']:
            if 'weight_limit' not in object:
                object['weight_limit'] = {}
            if not object['weight_limit'].get('free_limit'):
                object['weight_limit']['free_limit'] = float(t['weight_free_limit'])
            if 'slabs' not in object['weight_limit']:
                object['weight_limit']['slabs'] = []
            if t['weight_lower_limit']:
                weight_slab = {
                    'lower_limit': t['weight_lower_limit'],
                    'upper_limit': t['weight_upper_limit'],
                    'price': t['weight_limit_price'],
                    'currency': t['weight_limit_currency']
                }
                object['weight_limit']['slabs'].append(weight_slab)

            # object["weight_limit"]["free_limit"] = (
            #     object["weight_limit"]["free_limit"] or t["weight_free_limit"]
            # )
            # keys_to_extract = [
            #     "weight_lower_limit",
            #     "weight_upper_limit",
            #     "weight_limit_price",
            #     "weight_limit_currency",
            # ]
            # weight_slab = dict(
            #     filter(lambda item: item[0] in keys_to_extract, t.items())
            # )
            # del weight_slab["weight_lower_limit"]
            # weight_slab["lower_limit"] = weight_slab
            # del weight_slab["weight_upper_limit"]
            # weight_slab["upper_limit"] = weight_slab
            # del weight_slab["weight_limit_price"]
            # weight_slab["price"] = weight_slab
            # del weight_slab["weight_limit_currency"]
            # weight_slab["currency"] = weight_slab

            # if weight_slab["lower_limit"] is not None:
            #     object["weight_limit"]["slabs"].append(weight_slab)

        elif t['destination_detention_free_limit'] or t['destination_detention_lower_limit']:
            if 'destination_local' not in object:
                object['destination_local'] = {'detention': {}}
            if not object['destination_local']['detention'].get('free_limit'):
                object['destination_local']['detention']['free_limit'] = float(t['destination_detention_free_limit'])
            if 'slabs' not in object['destination_local']['detention']:
                object['destination_local']['detention']['slabs'] = []
            if t['destination_detention_lower_limit']:
                slab = {
                    'lower_limit': t['destination_detention_lower_limit'],
                    'upper_limit': t['destination_detention_upper_limit'],
                    'price': t['destination_detention_price'],
                    'currency': t['destination_detention_currency']
                }
                object['destination_local']['detention']['slabs'].append(slab)
            # object["destination_local"] = {"detention": {}}
            # object["destination_local"]["detention"]["free_limit"] = (
            #     object["destination_local"]["detention"]["free_limit"]
            #     or t["destination_detention_free_limit"]
            # )
            # object["destination_local"]["detention"]["slabs"] = (
            #     object["destination_local"]["detention"]["slabs"] or []
            # )
            # keys_to_extract = [
            #     "destination_detention_lower_limit",
            #     "destination_detention_upper_limit",
            #     "destination_detention_price",
            #     "destination_detention_currency",
            # ]
            # slab = dict(filter(lambda item: item[0] in keys_to_extract, t.items()))
            # del slab["destination_detention_lower_limit"]
            # slab["lower_limit"] = slab
            # del slab["destination_detention_upper_limit"]
            # slab["upper_limit"] = slab
            # del slab["destination_detention_price"]
            # slab["price"] = slab
            # del slab["destination_detention_currency"]
            # slab["currency"] = slab
            # if slab["lower_limit"] is not None:
            #     object["destination_local"]["detention"]["slabs"].append(slab)
    object["rate_sheet_id"] = params['rate_sheet_id']
    object["performed_by_id"] = created_by_id
    object["service_provider_id"] = params['service_provider_id']
    object["procured_by_id"] = procured_by_id
    object["sourced_by_id"] = sourced_by_id
    object["cogo_entity_id"] = params['cogo_entity_id']
    object["source"] = "rate_sheet"
    object["is_extended"] = False
    for line_items in object['line_items']:
        if line_items['price']:
            line_items['price'] = float(line_items['price'])
    request_params = object
    if 'extended_rates' in rows[0]:
        request_params["is_extended"] = True
    print(request_params, "sak final")
    # try:
    create_fcl_freight_rate_data(request_params)
    print("pass")
    if 'extended_rates' in rows[0]:
        request_params["extend_rates"] = True
        del request_params["is_extended"]
        extend_create_fcl_freight_rate_data(request_params)
    # except:
    #     print("fail")


def write_fcl_freight_local_object(params, rows, csv):
    object = {
        "trade_type": rows[0]["trade_type"],
        "port": rows[0]["port"],
        "main_port": rows[0]["main_port"],
        "container_size": rows[0]["container_size"],
        "container_type": rows[0]["container_type"],
        "commodity": rows[0]["commodity"],
        "shipping_line": rows[0]["shipping_line"],
        "data": {"line_items": []},
        "service_provider_id": params["service_provider_id"],
    }

    for t in rows[0:-1]:
        if t["code"]:
            line_item = {
                "location": t["location"],
                "code": t["code"],
                "unit": t["unit"],
                "price": t["price"],
                "currency": t["currency"],
                "remarks": [t["remark1"], t["remark2"], t["remark3"]].compact(),
                "slabs": [],
            }
            object["data"]["line_items"].append(line_item)
        else:
            slab = {
                "lower_limit": t["lower_limit"],
                "upper_limit": t["upper_limit"],
                "price": t["price"],
                "currency": t["currency"],
            }
            object["data"]["line_items"][-1]["slabs"].append(slab)

    # will have to create ValidateFclFreightObject seprately

    # object_validity = ValidateFclFreightObject.run!(module=params['module'], object=object)

    # if object_validity["valid"]:
    #     csv.writerow(rows[0].values())
    # else:
    #     csv.writerow(rows[0].values() + [", ".join(object_validity["errors"])])
    #     set_errors_present(True)

    # for t in rows[1:]:
    #     csv.writerow(t.values())

    # params.rates_count = int(params.rates_count) + 1


def process_fcl_freight_local(params):
    return


def create_fcl_freight_rate_local(params):
    return


def validate_fcl_freight_free_day(params):
    return


def write_fcl_freight_free_day_object(params):
    return


def process_fcl_freight_free_day(params):
    return


def create_fcl_freight_rate_free_day(params):
    return


def validate_fcl_freight_commodity_surcharge(params):
    return


def write_fcl_freight_commodity_surcharge_object(params):
    return


def process_fcl_freight_commodity_surcharge(params):
    return


def create_fcl_freight_rate_commodity_surcharge(params):
    return


def validate_fcl_freight_seasonal_surcharge(params):
    return


def write_fcl_freight_seasonal_surcharge_object(params):
    return


def process_fcl_freight_seasonal_surcharge(params):
    return


def create_fcl_freight_rate_seasonal_surcharge(params):
    return


def validate_fcl_freight_weight_limit(params):
    return


def write_fcl_freight_weight_limit_object(params):
    return


def process_fcl_freight_weight_limit(params):
    total_lines = 0
    return


def create_fcl_freight_rate_weight_limit(params):
    return


def get_location_id(q, country_code=None, service_provider_id=None):
    pincode_filters = {"type": "pincode", "postal_code": q, "status": "active"}
    if country_code is not None:
        pincode_filters = pincode_filters.merge({country_code: country_code})
    locations = client.ruby.list_locations(
        {"filters": pincode_filters, "fields": ["id"]}
    )["list"]
    if not locations:
        locations = client.ruby.list_locations(
            {
                "filters": {"type": "country", "country_code": q, "status": "active"},
                "fields": ["id"],
            }
        )["list"]
    seaport_filters = {"type": "seaport", "port_code": q, "status": "active"}
    if not locations:
        country_filters = {"type": "country", "country_code": q, "status": "active"}
        if country_code is not None:
            country_filters = {**country_filters, "country_code": country_code}
        locations = client.ruby.list_locations(filters=country_filters, fields=["id"])[
            "list"
        ]
    seaport_filters = {"type": "seaport", "port_code": q, "status": "active"}
    if country_code is not None:
        seaport_filters = {**seaport_filters, "country_code": country_code}
    locations = (
        client.ruby.list_locations(filters=seaport_filters, fields=["id"])["list"]
        if not locations
        else locations
    )
    airport_filters = {"type": "airport", "port_code": q, "status": "active"}
    if country_code is not None:
        airport_filters = {**airport_filters, "country_code": country_code}
    locations = (
        client.ruby.list_locations(filters=airport_filters, fields=["id"])["list"]
        if not locations
        else locations
    )
    name_filters = {"name": q, "status": "active"}
    if country_code is not None:
        name_filters = {**name_filters, "country_code": country_code}
    locations = (
        client.ruby.list_locations(filters=name_filters, fields=["id"])["list"]
        if not locations
        else locations
    )
    display_name_filters = {"display_name": q, "status": "active"}
    if country_code is not None:
        display_name_filters = {**display_name_filters, "country_code": country_code}
    locations = (
        client.ruby.list_locations(filters=display_name_filters, fields=["id"])["list"]
        if not locations
        else locations
    )
    # check
    if not locations:
        locations = client.ruby.list_ltl_freight_rate_zones(name=q, service_provider_id=service_provider_id).values_list('id', flat=True)
        return locations[0] if locations else None

    return locations[0]["id"] if locations else None



def get_location(location, type):
    if type == "port":
        location = client.ruby.list_locations(
            {"filters": {"type": "seaport", "port_code": location, "status": "active"}}
        )["list"][0]
    else:
        location = client.ruby.list_locations(
            {"filters": {"type": type, "name": location, "status": "active"}}
        )["list"][0]
    return


def get_importer_exporter_id(importer_exporter_name):
    importer_exporter_id = client.ruby.list_organizations(
        {
            "filters": {
                "account_type": "importer_exporter",
                "short_name": importer_exporter_name,
                "status": "active",
            }
        }
    )["list"][0]
    return importer_exporter_id


def validate_fcl_freight_freight(params):
    headers = [
        "origin_port",
        "origin_main_port",
        "destination_port",
        "destination_main_port",
        "container_size",
        "container_type",
        "commodity",
        "shipping_line",
        "validity_start",
        "validity_end",
        "code",
        "unit",
        "price",
        "currency",
        "extend_rates",
        "weight_free_limit",
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
        "remark1",
        "remark2",
        "remark3",
        "payment_term",
    ]
    total_lines = 0
    first_row = None
    path = get_original_file_path(params)
    first_row = None
    with open(path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            total_lines += 1
            if total_lines == 1:
                first_row = row
    print(total_lines, first_row, len(first_row), len(headers), len([i for i in first_row if i in headers]))
    set_total_line(params, total_lines)
    if len([i for i in first_row if i in headers]) != len(headers):
        params["status"] = "invalidated"
    print(params["status"])
    last_line = get_last_line(params)
    rows = []
    with open(get_file_path(params), 'a+', newline='') as csv_file:
        # reader = csv.reader(csv_file)
        csv_writer = csv.writer(csv_file)
        last_line = get_last_line(params)
        # print(last_line)
        if last_line == 0:
            csv_writer.writerow(headers)
        index = -1
        with open(get_original_file_path(params), "r") as csvfile:
                new_reader = csv.DictReader(csvfile)
                print(new_reader)
                for row in new_reader:
                    index += 1
                    # if index < last_line:
                    #     continue
                    print(row,'ss')
                    present_field = ['origin_port', 'destination_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'validity_start', 'validity_end', 'code', 'unit', 'price', 'currency']
                    blank_field = ['weight_free_limit','weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency', 'destination_detention_free_limit', 'destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency']
                    if valid_hash(row, present_field, blank_field):
                        print('y1')
                        if rows:
                            print(rows)
                            write_fcl_freight_freight_object(rows, csv_writer, params)
                            set_last_line(index, params)
                        # rows.append(row)
                        rows = [row]
                    elif rows and (
                        (valid_hash(
                            row,
                            ["code", "unit", "price", "currency"],
                            [
                                "origin_port",
                                "origin_main_port",
                                "destination_port",
                                "destination_main_port",
                                "container_size",
                                "container_type",
                                "commodity",
                                "shipping_line",
                                "validity_start",
                                "validity_end",
                                "weight_free_limit",
                                "weight_lower_limit",
                                "weight_upper_limit",
                                "weight_limit_price",
                                "weight_limit_currency",
                                "destination_detention_free_limit",
                                "destination_detention_lower_limit",
                                "destination_detention_upper_limit",
                                "destination_detention_price",
                                "destination_detention_currency",
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
                            ],
                        )
                    )):
                        rows.append(row)
                    else:
                        if rows:
                            write_fcl_freight_freight_object(rows, csv_writer, params)
                            set_last_line(index)
                        csv_writer.writerow(list(row.values()) + ['Incorrect Row'])
                        rows = []
        print(rows, "fineal_rows")
        with open("text.json", "w") as outfile:
            json.dump(rows, outfile)
        if rows:
            write_fcl_freight_freight_object(rows,csv_file, params)
            set_last_line(total_lines, params)
            return

    return


def write_fcl_freight_freight_object(rows, csv, params):
    print(rows, 'rows')
    print(params, 'params')
    object = {key: rows[0][key] for key in ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'validity_start', 'validity_end', 'schedule_type', 'payment_term']}
    print(object)
    object['validity_start'] = convert_date_format(object['validity_start'])
    object['validity_end'] = convert_date_format(object['validity_end'])
    print( object['validity_start'],  object['validity_end'], "date")
    object['line_items'] = []
    for t in rows:
        if t['code'] is not None:
            line_item = {key: t[key] for key in ['code', 'unit', 'price', 'currency']}
            line_item['remarks'] = [t['remark1'], t['remark2'], t['remark3']]
            line_item['remarks'] = list(filter(None, line_item['remarks']))
            line_item['slabs'] = []
            object['line_items'].append(line_item)
        elif t['weight_free_limit'] is not None or t['weight_lower_limit'] is not None:
            object['weight_limit'] = object['weight_limit'] or {}
            object['weight_limit']['free_limit'] = t['weight_free_limit'] or object['weight_limit']['free_limit']
            object['weight_limit']['slabs'] = [] or object['weight_limit']['slabs']
            weight_slab = {key: t[key] for key in ['weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency']}
            weight_slab['lower_limit'] = weight_slab.pop('weight_lower_limit')
            weight_slab['upper_limit'] = weight_slab.pop('weight_upper_limit')
            weight_slab['price'] = weight_slab.pop('weight_limit_price')
            weight_slab['currency'] = weight_slab.pop('weight_limit_currency')
            if weight_slab['lower_limit'] is not None:
                object['weight_limit']['slabs'].append(weight_slab)
        elif t['destination_detention_free_limit'] is not None or t['destination_detention_lower_limit'] is not None:
             object['destination_local'] =  object['destination_local'] or {'detention': {} }
             object['destination_local']['detention']['free_limit'] = object['destination_local']['detention']['free_limit'] or t['destination_detention_free_limit']
             object['destination_local']['detention']['slabs'] = [] or object['destination_local']['detention']['slabs']
             slab = {key: t[key] for key in ['destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency']}
             slab['lower_limit'] = slab.pop('destination_detention_lower_limit')
             slab['upper_limit'] = slab.pop('destination_detention_upper_limit')
             slab['price'] = slab.pop('destination_detention_price')
             slab['currency'] = slab.pop('destination_detention_currency')
             if slab['lower_limit'] is not None:
                object['destination_local']['detention']['slabs'].append(slab)

    object['service_provider_id'] = params['service_provider_id']
    object['cogo_entity_id'] = params['cogo_entity_id']
    return



def validate_fcl_freight_local(params):
   return




def validate_and_process_rate_sheet_converted_file(params):
    if params['status'] != 'converted':
        return
    print("params",params)
    reset_counters(params)
    for converted_file in params['converted_files']:
        reset_counters(converted_file)
        print("validate_{}_{}".format(converted_file['service_name'], converted_file['module']))
        getattr(process_rate_sheet, "validate_{}_{}".format(converted_file['service_name'], converted_file['module']))(
            params
        )
    if params['converted_files']:
        for converted_files in params['converted_files']:
            reset_counters(converted_files)
            validation_statuses = converted_files['status']

            if 'invalidated' in validation_statuses:
                params['status'] = 'uploaded'
                converted_files = delete_temp_data
            else:
                converted_files = mark_processing
                params['status'] = 'processing'
                # send_rate_sheet_notifications
                converted_files = delete_temp_data
                process_converted_files(params)


def process_converted_files(params):
    params['status'] = 'processing'
    initial_time = time.time()
    for converted_file in params['converted_files']:
        reset_counters(params)
        print("process_{}_{}".format(converted_file['service_name'], converted_file['module']))
        getattr(process_rate_sheet, "process_{}_{}".format(converted_file['service_name'], converted_file['module']))(
            params
        )
        final_time = time.time() -initial_time
        print(final_time, "final_time")
        print("done")
    params['status'] = 'complete'
    for _ in params['converted_files']:
        delete_temp_data
    # send_rate_sheet_notifications
    return

