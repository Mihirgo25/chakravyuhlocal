import os, csv, json, math
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from micro_services.client import *
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_seasonal_surcharge import create_fcl_freight_rate_seasonal_surcharge
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_weight_limit import create_fcl_freight_rate_weight_limit

from services.rate_sheet.interactions.upload_file import upload_media_file
from services.rate_sheet.interactions.validate_fcl_freight_object import validate_fcl_freight_object
from database.db_session import rd

from fastapi.encoders import jsonable_encoder

from datetime import datetime
import dateutil.parser as parser
from database.rails_db import get_shipping_line, get_organization
from services.rate_sheet.helpers import *

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
error_present_hash = "error_present"
processed_percent_hash = "process_percent"

def processed_percent_key(params):
    return f"rate_sheet_converted_file_processed_percent_{params['id']}"

def set_processed_percent(processed_percent, params):
    if rd:
        rd.hset(processed_percent_hash, processed_percent_key(params), processed_percent)


def get_processed_percent(params):
    if rd:
        try:
            cached_response = rd.hget(processed_percent_hash, processed_percent_key(params))
            return int(cached_response)
        except:
            return 0


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


# def delete_last_line(last_line_hash):
#     if rd:
#         rd.delete(last_line_hash, last_line_key)

def mark_processing(params, update):
    update.status = "processing"
    return params


def set_errors_present(errors_present, params):
    if rd:
        rd.hset(error_present_hash, errors_present_key(params), errors_present)

def get_errors_present(params):
    value = rd.hget(total_line_hash, errors_present_key(params))
    return str(value.decode('utf-8')) == 'true' if value is not None else False

def valid_hash(hash, present_fields=None, blank_fields=None):
    if present_fields:
        for field in present_fields:
            if field not in hash:
                return False
            if not hash[field]:
                return False
    if blank_fields:
        for field in blank_fields:
            if field not in hash:
                return True
            if hash[field]:
                return False
    return True

def get_port_id(port_code):
    filters =  {"filters":{"type": "seaport", "port_code": port_code, "status": "active"}}
    try:
        port_id =  maps.list_locations(filters)['list'][0]["id"]
    except:
        port_id = None
    return port_id


def get_airport_id(port_code, country_code):
    filters =  {"filters":{"type": "airport", "port_code": port_code, "status": "active", "country_code": country_code}}
    airport_id = maps.list_locations({'filters': str(filters)})['list'][0]["id"]
    return airport_id


def get_shipping_line_id(shipping_line_name):
    try:
        shipping_line_id = get_shipping_line(short_name=shipping_line_name)[0]['id']
    except:
        shipping_line_id = None
    return shipping_line_id


def get_airline_id(params):
    airline_id = common.list_operators(
        {"filters": {"id": params.origin_location_id}}
    )["list"][0]
    return airline_id


def convert_date_format(date):
    if not date:
        return date
    parsed_date = parser.parse(date, dayfirst=True)
    return datetime.strptime(str(parsed_date.date()), '%Y-%m-%d')



def append_in_final_csv(csv, row):
    list_opt = list(row.values())
    csv.writerow(list_opt)


def get_location_id(q, country_code = None, service_provider_id = None):
    pincode_filters =  {"type": "pincode", "postal_code": q, "status": "active"}
    if country_code is not None:
        pincode_filters['country_code'] = country_code
    locations = maps.list_locations({'filters': pincode_filters})['list']
    filters = {"type": "country", "country_code": q, "status": "active"}
    if not locations:
        locations = maps.list_locations({"filters": filters})['list']

    seaport_filters = {"type": "seaport", "port_code": q, "status": "active"}
    if not locations:
        country_filters = {"type": "country", "country_code": q, "status": "active"}
        if country_code is not None:
            country_filters["country_code"]= country_code
        locations = maps.list_locations({"filters": country_filters})['list']
    seaport_filters = {"type": "seaport", "port_code": q, "status": "active"}
    if country_code is not None:
        seaport_filters['country_code'] = country_code
    if not locations:
        locations = maps.list_locations({"filters":seaport_filters})['list']
    airport_filters = {"type": "airport", "port_code": q, "status": "active"}
    if country_code is not None:
        airport_filters['country_code'] = country_code
    if not locations:
        locations = maps.list_locations({"filters":airport_filters})['list']
    name_filters = {"name": q, "status": "active"}
    if country_code is not None:
        name_filters["country_code"] = country_code
    if not locations:
        locations = maps.list_locations({"filters": name_filters})['list']
    display_name_filters = {"display_name": q, "status": "active"}
    if country_code is not None:
        display_name_filters = maps.list_locations({"filters": display_name_filters})
    # if not locations:
    #     locations = common.list_ltl_freight_rate_zones(name=q, service_provider_id=service_provider_id).values_list('id', flat=True)
    #     return locations[0] if locations else None
    return locations[0]["id"] if locations else None



def get_location(location, type):
    if type == "port":
        location = maps.list_locations(
            {"filters": {"type": "seaport", "port_code": location, "status": "active"}, "includes": {"default_params_required": 1, "seaport_id": 1}}
        )["list"][0]
    else:
        location = maps.list_locations(
            {"filters": {"type": type, "name": location, "status": "active"}, "includes": {"default_params_required": 1, "seaport_id": 1}}
        )["list"][0]
    return location


def get_importer_exporter_id(importer_exporter_name):
    try:
        importer_exporter_id = get_organization(short_name=importer_exporter_name)[0]['id']
    except:
        importer_exporter_id = None
    return importer_exporter_id


def process_fcl_freight_local(params, converted_file, update):
    total_lines = 0
    original_path = get_original_file_path(converted_file)
    with open(original_path, encoding='iso-8859-1') as file:
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        headers = next(reader)
        for row in reader:
            total_lines += 1
    set_total_line(params, total_lines)

    last_line = get_last_line(params)
    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudit.get((RateSheetAudit.object_id == params["rate_sheet_id"]) & (RateSheetAudit.action_name == 'update') )
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']
    created_by_id = rate_sheet['performed_by_id']
    procured_by_id = rate_sheet['procured_by_id']
    sourced_by_id = rate_sheet['sourced_by_id']
    index = -1
    file_path = get_original_file_path(converted_file)
    edit_file = open(get_file_path(converted_file), 'w',newline="")
    last_row = []
    with open(file_path, encoding='iso-8859-1') as file:
        csv_writer = csv.writer(edit_file)
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        input_file = csv.DictReader(open(file_path))
        headers = input_file.fieldnames
        csv_writer.writerow(headers)
        for row in input_file:
            index += 1
            for k, v in row.items():
                if v == '':
                    row[k] = None
            present_field = ['trade_type', 'port', 'container_type', 'container_size', 'shipping_line', 'code', 'unit', 'price', 'currency']
            blank_field = ['lower_limit', 'upper_limit']
            if valid_hash(row, present_field, blank_field):
                if rows:
                    last_row = list(row.values())
                    create_fcl_freight_local_rate(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                    )
                    set_last_line(index, params)
                    # percent= (((converted_file.get('file_index') * 1.0) * get_last_line(params)) // (len(rate_sheet.get('data').get('converted_files'))) * get_total_line(params) )* 100
                    # set_processed_percent(percent, params)
                else:
                    list_opt = list(row.values())
                    csv_writer.writerow(list_opt)
                rows = [row]
            elif rows and (
                        (valid_hash(
                            row,
                            ["code", "unit", "price", "currency"],
                            ['trade_type', 'port', 'main_port', 'container_type', 'container_size', 'commodity', 'shipping_line', 'lower_limit', 'upper_limit']
                        )
                        or valid_hash(
                            row,
                            ['lower_limit', 'upper_limit', 'price', 'currency'],
                            ['trade_type', 'port', 'main_port', 'container_type', 'container_size', 'commodity', 'shipping_line', 'location', 'code', 'unit']
                        )
                    )):
                rows.append(row)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
            else:
                if rows:
                    last_row = list(row.values())
                    create_fcl_freight_local_rate(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                    )
                    set_last_line(index-1, params)
                    percent= (((converted_file.get('file_index') * 1.0) * get_last_line(params)) // (len(rate_sheet.get('data').get('converted_files'))) * get_total_line(params) )* 100
                    set_processed_percent(percent, params)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
                rows = []
    edit_file.flush()

    if not rows:
        return
    create_fcl_freight_local_rate(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row)
    converted_file['file_url'] = upload_media_file(get_file_path(converted_file))
    set_last_line(total_lines, params)
    percent= (((converted_file.get('file_index') * 1.0) * get_last_line(params)) // ((len(rate_sheet.get('data').get('converted_files'))) * total_lines))* 100
    converted_file['percent'] = percent
    set_processed_percent(percent, params)
    if math.ceil(percent)!=100:
        update.status = 'partially_complete'
        converted_file['status'] = 'partially_complete'
    else:
        update.status = 'complete'
        converted_file['status'] = 'complete'
    edit_file.close()
    try:
        os.remove(get_original_file_path(converted_file))
        os.remove(get_file_path(converted_file))
    except:
        return

def create_fcl_freight_local_rate(
    params, converted_file,  rows, created_by_id, procured_by_id, sourced_by_id, writer, last_row
):
    from celery_worker import celery_create_fcl_freight_rate_local
    keys_to_extract = ['trade_type', 'container_size', 'container_type', 'commodity']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    object['main_port_id'] = get_port_id(rows[0].get('main_port'))
    object['port_id'] = get_port_id(rows[0].get('port'))

    object["shipping_line_id"] = get_shipping_line_id(rows[0]["shipping_line"])
    object['data'] = { 'line_items': [] }
    object["line_items"] = []
    for t in rows:
        if t['code']:
            line_item = {
            'code': t['code'],
            'unit': t['unit'],
            'price': float(t['price']),
            'currency': t['currency'],
            'remarks': [t['remark1'], t['remark2'], t['remark3']] if any([t['remark1'], t['remark2'], t['remark3']]) else None,
            'slabs': []
            }
            line_item['location_id'] = get_location_id(t.get('location'))
            object['data']["line_items"].append(line_item)
        else:
            keys_to_extract = ['lower_limit', 'upper_limit', 'price', 'currency']
            slab = dict(filter(lambda item: item[0] in keys_to_extract, t.items()))
            keys_to_float = ['lower_limit', 'upper_limit', 'price']
            for key, val in slab.items():
                if key in keys_to_float:
                    slab[key] = float(val)
            object['data']['line_items'][-1]['slabs'].append(slab)

    request_params = object
    object["rate_sheet_id"] = params['rate_sheet_id']
    object["performed_by_id"] = created_by_id
    object["service_provider_id"] = params['service_provider_id']
    object["procured_by_id"] = procured_by_id
    object["sourced_by_id"] = sourced_by_id
    validation = write_fcl_freight_local_object(request_params, writer, params, converted_file, last_row)
    if validation.get('valid'):
        object['rate_sheet_validation'] = True
        celery_create_fcl_freight_rate_local.apply_async(kwargs={'request':request_params},queue='fcl_freight_rate')
    else:
        print(validation.get('error'))
    return validation



def write_fcl_freight_local_object(rows, csv, params, converted_file, last_row):
    object_validity = validate_fcl_freight_object(converted_file.get('module'), rows)
    if object_validity.get("valid"):
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




def write_fcl_freight_free_day_object(rows, csv, params,  converted_file, last_row):
    object_validity = validate_fcl_freight_object(converted_file.get('module'), rows)

    if object_validity.get("valid"):
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


def process_fcl_freight_free_day(params, converted_file, update):
    total_lines = 0
    original_path = get_original_file_path(converted_file)
    with open(original_path, encoding='iso-8859-1') as file:
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        headers = next(reader)
        for row in reader:
            total_lines += 1
    set_total_line(params, total_lines)

    last_line = get_last_line(params)
    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudit.get((RateSheetAudit.object_id == params["rate_sheet_id"]) & (RateSheetAudit.action_name == 'update') )
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']
    created_by_id = rate_sheet['performed_by_id']
    procured_by_id = rate_sheet['procured_by_id']
    sourced_by_id = rate_sheet['sourced_by_id']
    index = -1
    file_path = get_original_file_path(converted_file)
    edit_file = open(get_file_path(converted_file), 'w',newline="")
    last_row = []
    with open(file_path, encoding='iso-8859-1') as file:
        csv_writer = csv.writer(edit_file)
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        input_file = csv.DictReader(open(file_path))
        headers = input_file.fieldnames
        csv_writer.writerow(headers)
        for row in input_file:
            index += 1
            for k, v in row.items():
                if v == '':
                    row[k] = None
            present_field = ['location_type', 'location', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line', 'free_limit', 'specificity_type', 'previous_days_applicable']
            blank_field = ['lower_limit','upper_limit', 'price', 'currency']
            if valid_hash(row, present_field, blank_field) or valid_hash(row, ['location_type', 'location', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line', 'free_limit', 'specificity_type', 'previous_days_applicable', 'lower_limit', 'upper_limit', 'price', 'currency']):
                if rows:
                    last_row = list(row.values())
                    create_fcl_freight_rate_free_days(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                    )
                    set_last_line(index, params)
                    percent = (converted_file.get('file_index') * 1.0) // len(rate_sheet.get('data').get('converted_files'))* 100
                    set_processed_percent(percent, params)
                else:
                    list_opt = list(row.values())
                    csv_writer.writerow(list_opt)
                rows = [row]
            elif (
                valid_hash(
                    row,
                    ["lower_limit", "upper_limit", "price", "currency"],
                    [
                        "location_type",
                        "location",
                        "trade_type",
                        "free_days_type",
                        "container_size",
                        "container_type",
                        "shipping_line",
                        "free_limit",
                        "specificity_type",
                        "previous_days_applicable"
                    ],
                )
            ):
                rows.append(row)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
            else:
                if rows:
                    last_row = list(row.values())
                    create_fcl_freight_rate_free_days(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                    )
                    set_last_line(index-1, params)
                    percent= (((converted_file.get('file_index') * 1.0) * get_last_line(params)) // (len(rate_sheet.get('data').get('converted_files'))) * get_total_line(params) )* 100
                    set_processed_percent(percent, params)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
                rows = []
    edit_file.flush()
    if not rows:
        return
    create_fcl_freight_rate_free_days(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row)
    set_last_line(total_lines, params)
    valid = converted_file.get('valid_rates_count')
    total = converted_file.get('rates_count')
    percent_completed = (valid / total) * 100
    converted_file['file_url'] = upload_media_file(get_file_path(converted_file))
    percent= (converted_file.get('file_index') * 1.0) // len(rate_sheet.get('data').get('converted_files'))
    converted_file['percent'] = percent_completed
    set_processed_percent(percent, params)
    edit_file.close()
    if math.ceil(percent_completed)!=100:
        update.status = 'partially_complete'
        converted_file['status'] = 'partially_complete'
    else:
        update.status = 'complete'
        converted_file['status'] = 'complete'
    try:
        os.remove(get_original_file_path(converted_file))
        os.remove(get_file_path(converted_file))
    except:
        return

    return


def create_fcl_freight_rate_free_days(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row):
    from celery_worker import celery_create_fcl_freight_rate_free_day
    keys_to_extract = ['location_type', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'free_limit', 'specificity_type', 'previous_days_applicable']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    keys_to_float = ['lower_limit', 'upper_limit', 'price']
    for key, val in object.items():
        if key in keys_to_float:
            object[key] = float(val)
    location = get_location(rows[0]['location'], rows[0]['location_type'])
    object['location'] = location
    object['location_id'] = location['id']
    object['port_id'] = location.get('seaport_id')
    object['country_id'] = location.get('country_id')
    object['trade_id'] = location.get('trade_id')
    object['continent_id'] = location.get('continent_id')
    object['shipping_line_id'] = get_shipping_line_id(rows[0]['shipping_line'])
    object['importer_exporter_id'] = get_importer_exporter_id(rows[0]['importer_exporter'])
    object['remarks'] = [rows[0]['remark1'], rows[0]['remark2'], rows[0]['remark3']]
    object['slabs'] = []
    for t in rows:
        keys_to_extract = ['lower_limit', 'upper_limit', 'price', 'currency']
        slab = dict(filter(lambda item: item[0] in keys_to_extract, t.items()))
        keys_to_float = ['lower_limit', 'upper_limit', 'price']
        for key, val in slab.items():
            if key in keys_to_float:
                slab[key] = float(val)
        if object['slabs']:
            object['slabs'].append(slab)
    object['rate_sheet_id'] = params['rate_sheet_id']
    object['performed_by_id'] = created_by_id
    object['service_provider_id'] = params['service_provider_id']
    object['procured_by_id'] = procured_by_id
    object['sourced_by_id'] = sourced_by_id
    request_params = object
    validation = write_fcl_freight_free_day_object(request_params.copy(), csv_writer, params,  converted_file, last_row)
    if validation.get('valid'):
        object['rate_sheet_validation'] = True
        celery_create_fcl_freight_rate_free_day.apply_async(kwargs={'request':request_params},queue='fcl_freight_rate')
    else:
        print(validation.get('error'))
    return



def write_fcl_freight_commodity_surcharge_object(rows, csv, params, converted_file):
    object_validity = validate_fcl_freight_object(converted_file.get('module'), rows)
    if object_validity.get("valid"):
            converted_file['valid_rates_count'] = int(converted_file['valid_rates_count'])+1
    else:
        try:
            error = ["".join(str(object_validity.get("error")))]
            list_opt = error
            csv.writerow(list_opt)
        except:
            print('no csv')
    converted_file['rates_count'] = int(converted_file['rates_count'])+1
    return object_validity


def process_fcl_freight_commodity_surcharge(params, converted_file, update):
    total_lines = 0
    original_path = get_original_file_path(converted_file)
    with open(original_path, encoding='iso-8859-1') as file:
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        headers = next(reader)
        for row in reader:
            total_lines += 1
    set_total_line(params, total_lines)

    last_line = get_last_line(params)
    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudit.get((RateSheetAudit.object_id == params["rate_sheet_id"]) & (RateSheetAudit.action_name == 'update') )
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']
    created_by_id = rate_sheet['performed_by_id']
    procured_by_id = rate_sheet['procured_by_id']
    sourced_by_id = rate_sheet['sourced_by_id']
    index = -1
    file_path = get_original_file_path(converted_file)
    with open(file_path, encoding='iso-8859-1') as file:
        csv_writer = csv.writer(file)
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        if last_line == 0:
            csv_writer.writerow(headers)
        input_file = csv.DictReader(open(file_path))
        for row in input_file:
            index += 1
            for k, v in row.items():
                if v == '':
                    row[k] = None
            row = row
            last_line = get_last_line(params)
            present_field = ['origin_location', 'destination_location', 'container_size', 'container_type', 'shipping_line', 'code', 'price', 'currency']
            if valid_hash(row, present_field, None):
                create_fcl_freight_rate_commodity_surcharge(
                    params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id
                )
                set_last_line(index+1, params)
    return


def create_fcl_freight_rate_commodity_surcharge(params, converted_file, rows, created_by_id, sourced_by_id, procured_by_id):
    keys_to_extract = ['container_size', 'container_type', 'commodity', 'price', 'currency']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    object['origin_location_id'] = get_location_id(rows[0]['origin_location'])
    object['destination_location_id'] = get_location_id(rows[0]['destination_location'])
    object['shipping_line_id'] = get_shipping_line_id(rows[0]['shipping_line'])
    object['rate_sheet_id'] = params['rate_sheet_id']
    object['performed_by_id'] = created_by_id
    object['service_provider_id'] = params['service_provider_id']
    object['procured_by_id'] = procured_by_id
    object['sourced_by_id'] = sourced_by_id
    create_fcl_freight_rate_commodity_surcharge(object)
    return



def write_fcl_freight_seasonal_surcharge_object(rows, csv, params, converted_file):
    object_validity = validate_fcl_freight_object(converted_file.get('module'), rows)
    if object_validity.get("valid"):
            converted_file['valid_rates_count'] = int(converted_file['valid_rates_count'])+1
    else:
        try:
            error = ["".join(str(object_validity.get("error")))]
            list_opt = error
            csv.writerow(list_opt)
        except:
            print('no csv')
    converted_file['rates_count'] = int(converted_file['rates_count'])+1
    return object_validity


def process_fcl_freight_seasonal_surcharge(params, converted_file, update):
    total_lines = 0
    original_path = get_original_file_path(converted_file)
    with open(original_path, encoding='iso-8859-1') as file:
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        headers = next(reader)
        for row in reader:
            total_lines += 1
    set_total_line(params, total_lines)

    last_line = get_last_line(params)
    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudit.get((RateSheetAudit.object_id == params["rate_sheet_id"]) & (RateSheetAudit.action_name == 'update') )
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']
    created_by_id = rate_sheet['performed_by_id']
    procured_by_id = rate_sheet['procured_by_id']
    sourced_by_id = rate_sheet['sourced_by_id']
    index = -1
    file_path = get_original_file_path(converted_file)
    with open(file_path, encoding='iso-8859-1') as file:
        csv_writer = csv.writer(file)
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        if last_line == 0:
            csv_writer.writerow(headers)
        input_file = csv.DictReader(open(file_path))
        for row in input_file:
            index += 1
            for k, v in row.items():
                if v == '':
                    row[k] = None
            row = row
            last_line = get_last_line(params)
            present_field = ['origin_location', 'destination_location', 'container_size', 'container_type', 'shipping_line', 'code', 'price', 'currency', 'validity_start', 'validity_end']
            if valid_hash(row, present_field, None):
                create_fcl_freight_rate_seasonal_surcharges(
                    params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id
                )
                set_last_line(index, params)




def create_fcl_freight_rate_seasonal_surcharges(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id):
    keys_to_extract = ['container_size', 'container_type', 'free_limit', 'code', 'price', 'currency', 'validity_start', 'validity_end']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    object['validity_start'] = convert_date_format(object['validity_start'])
    object['validity_end'] = convert_date_format(object['validity_end'])
    object['origin_location_id'] = get_location_id(rows[0]['origin_location'])
    object['destination_location_id'] = get_location_id(rows[0]['destination_location'])
    object['shipping_line_id'] = get_shipping_line_id(rows[0]['shipping_line'])
    object['rate_sheet_id'] = params['rate_sheet_id']
    object['performed_by_id'] = created_by_id
    object['service_provider_id'] = params['service_provider_id']
    object['procured_by_id'] = procured_by_id
    object['sourced_by_id'] = sourced_by_id
    create_fcl_freight_rate_seasonal_surcharge(object)
    return



def write_fcl_freight_weight_limit_object(rows, csv, params, converted_file):
    object_validity = validate_fcl_freight_object(converted_file.get('module'), rows)
    if object_validity.get("valid"):
            converted_file['valid_rates_count'] = int(converted_file['valid_rates_count'])+1
    else:
        try:
            error = ["".join(str(object_validity.get("error")))]
            list_opt = error
            csv.writerow(list_opt)
        except:
            print('no csv')
    converted_file['rates_count'] = int(converted_file['rates_count'])+1
    return object_validity



def process_fcl_freight_weight_limit(params, converted_file, update):
    total_lines = 0
    original_path = get_original_file_path(converted_file)
    with open(original_path, encoding='iso-8859-1') as file:
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        headers = next(reader)
        for row in reader:
            total_lines += 1
    set_total_line(params, total_lines)

    last_line = get_last_line(params)
    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudit.get((RateSheetAudit.object_id == params["rate_sheet_id"]) & (RateSheetAudit.action_name == 'update') )
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']
    created_by_id = rate_sheet['performed_by_id']
    procured_by_id = rate_sheet['procured_by_id']
    sourced_by_id = rate_sheet['sourced_by_id']
    index = -1
    file_path = get_original_file_path(converted_file)
    with open(file_path, encoding='iso-8859-1') as file:
        csv_writer = csv.writer(file)
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        if last_line == 0:
            csv_writer.writerow(headers)
        input_file = csv.DictReader(open(file_path))
        for row in input_file:
            index += 1
            for k, v in row.items():
                if v == '':
                    row[k] = None
            last_line = get_last_line(params)
            present_field = ['origin_location', 'destination_location', 'container_size', 'container_type', 'shipping_line', 'free_limit']
            blank_field = ['lower_limit','upper_limit', 'price', 'currency']
            if valid_hash(row, present_field, blank_field) or valid_hash(row, ['origin_location', 'destination_location', 'container_size', 'container_type', 'shipping_line', 'free_limit', 'lower_limit', 'upper_limit', 'price', 'currency']):
                if rows:
                    create_fcl_freight_rate_weight_limits(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id
                    )
                    set_last_line(index, params)
                    percent = (converted_file.get('file_index') * 1.0) // len(rate_sheet.get('data').get('converted_files'))* 100
                    set_processed_percent(percent, params)
                rows = [row]
            elif (
                valid_hash(
                    row,
                    ["lower_limit", "upper_limit", "price", "currency"],
                    [
                        "origin_location",
                        "destination_location",
                        "container_size",
                        "container_type",
                        "shipping_line",
                        "free_limit"
                    ],
                )
            ):
                rows.append(row)

    if not rows:
        return
    converted_file['file_url'] = upload_media_file(get_file_path(params))
    try:
        os.remove(get_original_file_path(converted_file))
        os.remove(get_file_path(converted_file))
    except:
        return
    create_fcl_freight_rate_weight_limits(params,converted_file, rows, created_by_id, procured_by_id, sourced_by_id)
    set_last_line(total_lines, params)
    percent= (converted_file.get('file_index') * 1.0) // len(rate_sheet.get('data').get('converted_files'))
    set_processed_percent(percent, params)
    if math.ceil(percent)!=100:
        update.status = 'partially_complete'
        converted_file['status'] = 'partially_complete'
    else:
        update.status = 'complete'
        converted_file['status'] = 'complete'


def create_fcl_freight_rate_weight_limits(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id):
    keys_to_extract = ['container_size', 'container_type', 'free_limit']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    object['origin_location_id'] = get_location_id(rows[0]['origin_location'])
    object['destination_location_id'] = get_location_id(rows[0]['destination_location'])
    object['shipping_line_id'] = get_shipping_line_id(rows[0]['shipping_line'])
    object['slabs'] = []
    for t in rows:
        keys_to_extract = ['lower_limit', 'upper_limit', 'price', 'currency']
        slab = dict(filter(lambda item: item[0] in keys_to_extract, t.items()))
        if slab:
            object['slabs'].append(slab)
    object['rate_sheet_id'] = params['rate_sheet_id']
    object['performed_by_id'] = created_by_id
    object['service_provider_id'] = params['service_provider_id']
    object['procured_by_id'] = procured_by_id
    object['sourced_by_id'] = sourced_by_id
    create_fcl_freight_rate_weight_limit(object)

def write_fcl_freight_freight_object(rows, csv, params,  converted_file, last_row):
    object_validity = validate_fcl_freight_object(converted_file.get('module'), rows)
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

def process_fcl_freight_freight(params, converted_file, update):
    total_lines = 0
    original_path = get_original_file_path(converted_file)
    with open(original_path, encoding='iso-8859-1') as file:
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        headers = next(reader)
        for row in reader:
            total_lines += 1
    set_total_line(params, total_lines)
    last_line = get_last_line(params)
    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudit.get((RateSheetAudit.object_id == params["rate_sheet_id"]) & (RateSheetAudit.action_name == 'update') )
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']
    created_by_id = rate_sheet['performed_by_id']
    procured_by_id = rate_sheet['procured_by_id']
    sourced_by_id = rate_sheet['sourced_by_id']
    index = -1
    file_path = get_original_file_path(converted_file)
    edit_file = open(get_file_path(converted_file), 'w')
    last_row = []
    with open(file_path, encoding='iso-8859-1') as file:
        csv_writer = csv.writer(edit_file)
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        input_file = csv.DictReader(open(file_path))
        headers = input_file.fieldnames
        csv_writer.writerow(headers)
        for row in input_file:
            index += 1
            for k, v in row.items():
                if v == '':
                    row[k] = None
            present_field = ['origin_port', 'destination_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'validity_start', 'validity_end', 'code', 'unit', 'price', 'currency']
            blank_field = ['weight_free_limit','weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency', 'destination_detention_free_limit', 'destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency']
            if valid_hash(row, present_field, blank_field):
                if rows:
                    last_row = list(row.values())
                    create_fcl_freight_freight_rate(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                    )
                    set_last_line(index-1, params)
                    percent= (((converted_file.get('file_index') * 1.0) * get_last_line(params)) // (len(rate_sheet.get('data').get('converted_files'))) * get_total_line(params) )* 100
                    set_processed_percent(percent, params)
                else:
                    list_opt = list(row.values())
                    csv_writer.writerow(list_opt)
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
                rows.append(row)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
            else:
                if rows:
                    last_row = list(row.values())
                    create_fcl_freight_freight_rate(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                    )
                    set_last_line(index-1, params)
                    percent= (((converted_file.get('file_index') * 1.0) * get_last_line(params)) // (len(rate_sheet.get('data').get('converted_files'))) * get_total_line(params) )* 100
                    set_processed_percent(percent, params)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
                rows = []
    edit_file.flush()
    if not rows:
        return
    create_fcl_freight_freight_rate(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row)
    set_last_line(total_lines, params)
    valid = converted_file.get('valid_rates_count')
    total = converted_file.get('rates_count')
    percent_completed = (valid / total) * 100
    # percent= (((converted_file.get('file_index') * 1.0) * get_last_line(params)) // ((len(rate_sheet.get('data').get('converted_files'))) * total_lines))* 100
    converted_file['percent'] = percent_completed
    converted_file['file_url'] = upload_media_file(get_file_path(converted_file))
    edit_file.close()
    if math.ceil(percent_completed)!=100:
        update.status = 'partially_complete'
        converted_file['status'] = 'partially_complete'
    else:
        update.status = 'complete'
    converted_file['status'] = 'complete'

    set_processed_percent(percent_completed, params)
    try:
        os.remove(get_original_file_path(converted_file))
        os.remove(get_file_path(converted_file))
    except:
        return

def create_fcl_freight_freight_rate(
    params, converted_file,  rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
):
    from celery_worker import create_fcl_freight_rate_delay, celery_extend_create_fcl_freight_rate_data
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
        if rows[0][port]:
            object[f"{str(port)}_id"] = get_port_id(rows[0][port])
    if rows[0]["shipping_line"]:
        object["shipping_line_id"] = get_shipping_line_id(rows[0]["shipping_line"])
    object["line_items"] = []
    for t in rows:
        if t['code']:
            line_item = {
            'code': t['code'],
            'unit': t['unit'],
            'price': float(t['price']),
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
                    'lower_limit': float(t['weight_lower_limit']),
                    'upper_limit': float(t['weight_upper_limit']),
                    'price': float(t['weight_limit_price']),
                    'currency': t['weight_limit_currency']
                }
                object['weight_limit']['slabs'].append(weight_slab)


        elif t['destination_detention_free_limit'] or t['destination_detention_lower_limit']:
            if 'destination_local' not in object:
                object['destination_local'] = {'detention': {}}
            if not object['destination_local']['detention'].get('free_limit'):
                object['destination_local']['detention']['free_limit'] = float(t['destination_detention_free_limit'])
            if 'slabs' not in object['destination_local']['detention']:
                object['destination_local']['detention']['slabs'] = []
            if t['destination_detention_lower_limit']:
                slab = {
                    'lower_limit': float(t['destination_detention_lower_limit']),
                    'upper_limit': float(t['destination_detention_upper_limit']),
                    'price': float(t['destination_detention_price']),
                    'currency': t['destination_detention_currency']
                }
                object['destination_local']['detention']['slabs'].append(slab)
    object["rate_sheet_id"] = params['rate_sheet_id']
    object["performed_by_id"] = created_by_id
    if params['service_provider_id']:
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
    if 'extend_rates' in rows[0]:
        request_params["is_extended"] = True
    validation = write_fcl_freight_freight_object(request_params, csv_writer, params, converted_file, last_row)
    if validation.get('valid'):
        object['rate_sheet_validation'] = True
        create_fcl_freight_rate_delay.apply_async(kwargs={'request':object},queue='fcl_freight_rate')
        if rows[0].get('extend_rates'):
            request_params['extend_rates'] = True
            celery_extend_create_fcl_freight_rate_data.apply_async(kwargs={'request':object},queue='fcl_freight_rate')
    else:
        print(validation.get('error'))
