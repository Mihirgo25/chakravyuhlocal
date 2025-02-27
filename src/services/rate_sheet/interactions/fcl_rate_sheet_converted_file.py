import os, csv, json, math
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from micro_services.client import *
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_seasonal_surcharge import create_fcl_freight_rate_seasonal_surcharge
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_weight_limit import create_fcl_freight_rate_weight_limit
from services.fcl_freight_rate.interaction.get_suggested_cogo_assured_fcl_freight_rates import get_suggested_cogo_assured_fcl_freight_rates
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

from services.rate_sheet.interactions.upload_file import upload_media_file
from services.rate_sheet.interactions.validate_fcl_freight_object import validate_fcl_freight_object
from database.db_session import rd

from fastapi.encoders import jsonable_encoder
from database.rails_db import get_organization
from services.rate_sheet.helpers import *
import chardet
from libs.parse_numeric import parse_numeric
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


def append_in_final_csv(csv, row):
    list_opt = list(row.values())
    csv.writerow(list_opt)


def get_location(location_code, type):
    location = {
        'id': None
    }
    if type == "port":
        location_list = maps.list_locations(
            {"filters": {"type": "seaport", "port_code": location_code, "status": "active"}, "includes": {"default_params_required": 1, "seaport_id": 1}}
        )
        if 'list' in location_list and len(location_list['list']) > 0:
            location = location_list['list'][0]
    else:
        location_list = maps.list_locations(
            {"filters": {"type": type, "country_code": location_code, "status": "active"}, "includes": {"default_params_required": 1, "seaport_id": 1}}
        )
        if 'list' in location_list and len(location_list['list']) > 0:
            location = location_list['list'][0]
    return location


def get_importer_exporter_id(importer_exporter_name):
    try:
        importer_exporter_id = get_organization(short_name=importer_exporter_name)[0]['id']
    except:
        importer_exporter_id = None
    return importer_exporter_id


def process_fcl_freight_local(params, converted_file, update):
    valid_headers = ["trade_type", "port", "main_port", "terminal", "container_size", "container_type", "commodity", "shipping_line", "location", "code", "unit", "lower_limit", "upper_limit", "price", "currency","market_price", "remark1", "remark2", "remark3", "rate_type"]
    total_lines = 0
    original_path = get_original_file_path(converted_file)

    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudit.get((RateSheetAudit.object_id == params["rate_sheet_id"]) & (RateSheetAudit.action_name == 'update') )
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']
    created_by_id = rate_sheet['performed_by_id']
    procured_by_id = rate_sheet['procured_by_id']
    sourced_by_id = rate_sheet['sourced_by_id']
    index = -1
    edit_file = open(get_file_path(converted_file), 'w')
    file_path = original_path
    last_row = []
    invalidated = False
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']
    with open(original_path, mode='rt', encoding=encoding) as file:
        csv_writer = csv.writer(edit_file)
        input_file = csv.DictReader(file)
        headers = input_file.fieldnames

        if len(set(valid_headers)&set(headers))!=len(valid_headers):
            error_file = ['invalid header']
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
                if v == '':
                    row[k] = None
            present_field = ['trade_type', 'port', 'container_type', 'container_size', 'shipping_line', 'code', 'unit', 'price', 'currency']
            blank_field = ['lower_limit', 'upper_limit']

            is_main_rate_row = False
            if row['port']:
                is_main_rate_row = True
            if valid_hash(row, present_field, blank_field):
                if rows:
                    last_row = list(row.values())
                    if is_previous_rate_valid:
                        create_fcl_freight_local_rate(
                            params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                        )
                    else:
                        is_previous_rate_valid = True
                    set_current_processing_line(index, converted_file)
                    percent= ((get_current_processing_line(converted_file) / total_lines)* 100)
                    set_processed_percent(percent, params)
                else:
                    list_opt = list(row.values())
                    csv_writer.writerow(list_opt)
                rows = [row]
            elif rows and (
                        (valid_hash(
                            row,
                            ["code", "unit", "price", "currency"],
                            ['trade_type', 'port', 'main_port', 'terminal', 'container_type', 'container_size', 'commodity', 'shipping_line', 'lower_limit', 'upper_limit', 'market_price']
                        )
                        or valid_hash(
                            row,
                            ['lower_limit', 'upper_limit', 'price', 'currency'],
                            ['trade_type', 'port', 'main_port', 'terminal', 'container_type', 'container_size', 'commodity', 'shipping_line', 'location', 'code', 'unit','market_price']
                        )
                    )):
                rows.append(row)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
            else:
                list_opt = []
                if rows and is_previous_rate_valid and is_main_rate_row:
                    last_row = list(row.values())
                    create_fcl_freight_local_rate(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                    )
                    set_current_processing_line(index-1, converted_file)
                    percent= ((get_current_processing_line(converted_file) / total_lines)* 100)
                    set_processed_percent(percent, params)
                else:
                    list_opt = list(row.values())
                list_opt.append('Invalid Row')
                csv_writer.writerow(list_opt)
                if is_previous_rate_valid:
                    converted_file['rates_count']+=1
                is_previous_rate_valid = False
                rows = []

    if rows and is_previous_rate_valid and not invalidated:
        create_fcl_freight_local_rate(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, '')
    edit_file.flush()
    converted_file['file_url'] = upload_media_file(get_file_path(converted_file))
    set_current_processing_line(total_lines, params)
    percent= ((get_current_processing_line(converted_file) / total_lines)* 100)
    try:
        valid = converted_file.get('valid_rates_count')
        total = converted_file.get('rates_count')
        percent_completed = (valid / total) * 100
    except:
        valid = 0
        total = 0
        percent_completed = 0
    converted_file['percent'] = percent_completed
    set_processed_percent(percent_completed, params)
    if valid == total and total!=0:
        update.status = 'complete'
        converted_file['status'] = 'complete'
    elif valid==0:
        update.status = 'uploaded'
        converted_file['status'] = 'invalidated'
    else:
        update.status = 'partially_complete'
        converted_file['status'] = 'partially_complete'
    edit_file.close()
    try:
        os.remove(get_original_file_path(converted_file))
        os.remove(get_file_path(converted_file))
    except:
        return

def create_fcl_freight_local_rate(
    params, converted_file,  rows, created_by_id, procured_by_id, sourced_by_id, writer, last_row
):
    from services.fcl_freight_rate.fcl_celery_worker import celery_create_fcl_freight_rate_local
    keys_to_extract = ['trade_type', 'container_size', 'container_type', 'commodity']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    object['main_port_id'] = get_port_id(rows[0].get('main_port'))
    object['terminal_id'] = get_terminal_id(rows[0].get('terminal'))
    object['port_id'] = get_port_id(rows[0].get('port'))
    object['rate_type'] = rows[0].get('rate_type') or DEFAULT_RATE_TYPE

    object["shipping_line_id"] = get_shipping_line_id(rows[0].get("shipping_line"))
    object['data'] = { 'line_items': [] }
    object["line_items"] = []
    for t in rows:
        if t['code'] and t.get('price'):
            line_item = {
            'code': t.get('code'),
            'unit': t.get('unit'),
            'price': parse_numeric(t.get('price')),
            'market_price': parse_numeric(t.get('market_price')),
            'currency': t.get('currency'),
            'remarks': [t.get('remark1'), t.get('remark2'), t.get('remark3')] if any([t.get('remark1'), t.get('remark2'), t.get('remark3')]) else None,
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
                    if val:
                        slab[key] = parse_numeric(val)
            object['data']['line_items'][-1]['slabs'].append(slab)

    request_params = object
    object["rate_sheet_id"] = params['rate_sheet_id']
    object["performed_by_id"] = created_by_id
    object["service_provider_id"] = params['service_provider_id']
    object["procured_by_id"] = procured_by_id
    object["sourced_by_id"] = sourced_by_id
    object["source"] = "rate_sheet"
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
    valid_headers = ["location_type", "location", "trade_type", "free_days_type", "container_size", "container_type", "shipping_line", "importer_exporter", "free_limit", "lower_limit", "upper_limit", "price", "currency", "specificity_type", "previous_days_applicable", "validity_start", "validity_end", "remark1", "remark2", "remark3"]

    total_lines = 0
    original_path = get_original_file_path(converted_file)
    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudit.get((RateSheetAudit.object_id == params["rate_sheet_id"]) & (RateSheetAudit.action_name == 'update') )
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']
    created_by_id = rate_sheet['performed_by_id']
    procured_by_id = rate_sheet['procured_by_id']
    sourced_by_id = rate_sheet['sourced_by_id']
    index = -1
    file_path = original_path
    edit_file = open(get_file_path(converted_file), 'w')
    last_row = []
    invalidated = False
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']
    with open(original_path, mode='rt', encoding=encoding) as file:
        csv_writer = csv.writer(edit_file)
        input_file = csv.DictReader(file)
        headers = input_file.fieldnames

        if len(set(valid_headers)&set(headers))!=len(valid_headers):
            error_file = ['invalid header']
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
                if v == '':
                    row[k] = None
            present_field = ['location_type', 'location', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line', 'free_limit', 'specificity_type', 'previous_days_applicable', 'validity_start', 'validity_end']
            blank_field = ['lower_limit','upper_limit', 'price', 'currency']
            is_main_rate_row = False
            if row['location_type']:
                is_main_rate_row = True
            if valid_hash(row, present_field, blank_field) or valid_hash(row, ['location_type', 'location', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line', 'free_limit', 'specificity_type', 'previous_days_applicable', 'lower_limit', 'upper_limit', 'price', 'currency', 'validity_start', 'validity_end']):
                if rows:
                    last_row = list(row.values())
                    if is_previous_rate_valid:
                        create_fcl_freight_rate_free_days(
                            params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                        )
                    else:
                        is_previous_rate_valid = True
                    set_current_processing_line(index, converted_file)
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
                        "previous_days_applicable",
                        "validity_start",
                        "validity_end"
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
                    create_fcl_freight_rate_free_days(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                    )
                    set_current_processing_line(index-1, converted_file)
                    percent= (((converted_file.get('file_index') * 1.0) * get_current_processing_line(converted_file)) // (len(rate_sheet.get('data').get('converted_files'))) * get_total_line(converted_file) )* 100
                    set_processed_percent(percent, params)
                else:
                    list_opt = list(row.values())
                list_opt.append('Invalid Row')
                csv_writer.writerow(list_opt)
                if is_previous_rate_valid:
                    converted_file['rates_count']+=1
                is_previous_rate_valid = False
                rows = []
    if rows and is_previous_rate_valid and not invalidated:
        create_fcl_freight_rate_free_days(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, '')
    set_current_processing_line(total_lines, converted_file)
    try:
        valid = converted_file.get('valid_rates_count')
        total = converted_file.get('rates_count')
        percent_completed = (valid / total) * 100
    except:
        valid = 0
        total = 0
        percent_completed = 0
    edit_file.flush()
    converted_file['file_url'] = upload_media_file(get_file_path(converted_file))
    percent= (converted_file.get('file_index') * 1.0) // len(rate_sheet.get('data').get('converted_files'))
    converted_file['percent'] = percent_completed
    set_processed_percent(percent_completed, params)
    edit_file.close()
    if valid == total and total!=0:
        update.status = 'complete'
        converted_file['status'] = 'complete'
    elif valid == 0:
        update.status = 'uploaded'
        converted_file['status'] = 'invalidated'
    else:
        update.status = 'partially_complete'
        converted_file['status'] = 'partially_complete'
    try:
        os.remove(get_original_file_path(converted_file))
        os.remove(get_file_path(converted_file))
    except:
        return

    return


def create_fcl_freight_rate_free_days(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row):
    from services.fcl_freight_rate.fcl_celery_worker import celery_create_fcl_freight_rate_free_day
    keys_to_extract = ['location_type', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'free_limit', 'specificity_type', 'previous_days_applicable', 'validity_start', 'validity_end']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    keys_to_float = ['lower_limit', 'upper_limit', 'price']
    for key, val in object.items():
        if key in keys_to_float:
            if val:
                object[key] = parse_numeric(val)
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
    object['validity_start'] = convert_date_format(object['validity_start'])
    object['validity_end'] = convert_date_format(object['validity_end'])
    slabs = []
    for t in rows:
        keys_to_extract = ['lower_limit', 'upper_limit', 'price', 'currency']
        slab = dict(filter(lambda item: item[0] in keys_to_extract, t.items()))
        keys_to_float = ['lower_limit', 'upper_limit', 'price']
        for key, val in slab.items():
            if key in keys_to_float:
                if val:
                    slab[key] = parse_numeric(val)
            filtered_slab = dict((key, value) for key, value in slab.items() if value is not None)
        if filtered_slab:
            slabs.append(filtered_slab)

    object['slabs'] = list(filter(None, slabs))
    object['rate_sheet_id'] = params['rate_sheet_id']
    object['performed_by_id'] = created_by_id
    object['service_provider_id'] = params['service_provider_id']
    object['procured_by_id'] = procured_by_id
    object['sourced_by_id'] = sourced_by_id
    object["source"] = "rate_sheet"
    if object['previous_days_applicable'].strip().lower() == 'false':
        object['previous_days_applicable'] = False
    else:
        object['previous_days_applicable'] = True
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
    set_total_line(converted_file, total_lines)

    last_line = get_current_processing_line(converted_file)
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
            last_line = get_current_processing_line(converted_file)
            present_field = ['origin_location', 'destination_location', 'container_size', 'container_type', 'shipping_line', 'code', 'price', 'currency']
            if valid_hash(row, present_field, None):
                create_fcl_freight_rate_commodity_surcharge(
                    params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id
                )
                set_current_processing_line(index+1, converted_file)
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
    set_total_line(converted_file, total_lines)

    last_line = get_current_processing_line(converted_file)
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
            last_line = get_current_processing_line(converted_file)
            present_field = ['origin_location', 'destination_location', 'container_size', 'container_type', 'shipping_line', 'code', 'price', 'currency', 'validity_start', 'validity_end']
            if valid_hash(row, present_field, None):
                create_fcl_freight_rate_seasonal_surcharges(
                    params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id
                )
                set_current_processing_line(index, converted_file)




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
    set_total_line(converted_file, total_lines)

    last_line = get_current_processing_line(converted_file)
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
            last_line = get_current_processing_line(converted_file)
            present_field = ['origin_location', 'destination_location', 'container_size', 'container_type', 'shipping_line', 'free_limit']
            blank_field = ['lower_limit','upper_limit', 'price', 'currency']
            if valid_hash(row, present_field, blank_field) or valid_hash(row, ['origin_location', 'destination_location', 'container_size', 'container_type', 'shipping_line', 'free_limit', 'lower_limit', 'upper_limit', 'price', 'currency']):
                if rows:
                    create_fcl_freight_rate_weight_limits(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id
                    )
                    set_current_processing_line(index, converted_file)
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
    set_current_processing_line(total_lines, converted_file)
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
    valid_headers = ["origin_port", "origin_main_port", "destination_port", "destination_main_port", "container_size", "container_type", "commodity", "shipping_line", "validity_start", "validity_end", "code", "unit", "price", "currency", "market_price", "extend_rates", "weight_free_limit", "weight_lower_limit", "weight_upper_limit", "weight_limit_price", "weight_limit_currency", "destination_detention_free_limit", "destination_detention_lower_limit", "destination_detention_upper_limit", "destination_detention_price", "destination_detention_currency", "schedule_type", "remark1", "remark2", "remark3", "payment_term", "rate_type"]
    total_lines = 0
    original_path = get_original_file_path(converted_file)
    rows = []
    params["rate_sheet_id"] = params["id"]
    rate_sheet = RateSheetAudit.get((RateSheetAudit.object_id == params["rate_sheet_id"]) & (RateSheetAudit.action_name == 'update') )
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']
    created_by_id = rate_sheet['performed_by_id']
    procured_by_id = rate_sheet['procured_by_id']
    sourced_by_id = rate_sheet['sourced_by_id']
    index = -1
    file_path = original_path
    edit_file = open(get_file_path(converted_file), 'w')
    last_row = []
    invalidated = False
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']

    with open(original_path, mode='rt', encoding=encoding) as file:
        # Read converted file for porcessing
        csv_writer = csv.writer(edit_file)
        input_file = csv.DictReader(file)
        headers = input_file.fieldnames

        if len(set(valid_headers) & set(headers)) != len(valid_headers):
            error_file = ['invalid header']
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
            if not ''.join([str(value) for value in row.values() if value is not None]).strip():
                continue
            for k, v in row.items():
                if v == '':
                    row[k] = None
            present_field = ['origin_port', 'destination_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'validity_start', 'validity_end', 'code', 'unit', 'price', 'currency', 'schedule_type']
            blank_field = ['weight_free_limit','weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency', 'destination_detention_free_limit', 'destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency']

            is_main_rate_row = False
            if row['origin_port']:
                is_main_rate_row = True

            if valid_hash(row, present_field, blank_field):
                if rows:
                    last_row = list(row.values())
                    # Create previous rate if previous rate was valid
                    if is_previous_rate_valid:
                        create_fcl_freight_freight_rate(
                            params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                        )
                    else:
                        is_previous_rate_valid = True
                    # Set Processing percent
                    set_current_processing_line(index-1, converted_file)
                    percent=  ((get_current_processing_line(converted_file) / total_lines)* 100)
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
                        "schedule_type",
                        "payment_term",
                        "rate_type",
                        "market_price"
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
                        "market_price"
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
                        "market_price"
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
                        "market_price"
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
                        "market_price"
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
                        "market_price"
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
                        "market_price"
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
                    create_fcl_freight_freight_rate(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                    )
                    set_current_processing_line(index-1, converted_file)
                    percent=  ((get_current_processing_line(converted_file) / total_lines)* 100)
                    set_processed_percent(percent, params)
                else:
                    list_opt = list(row.values())
                list_opt.append('Invalid Row')
                csv_writer.writerow(list_opt)
                if is_previous_rate_valid:
                    converted_file['rates_count']+=1
                is_previous_rate_valid = False
                rows = []
    if rows and is_previous_rate_valid and not invalidated:
        create_fcl_freight_freight_rate(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, '')
    set_current_processing_line(total_lines, converted_file)
    try:
        valid = converted_file.get('valid_rates_count')
        total = converted_file.get('rates_count')
        percent_completed = (valid / total) * 100
    except:
        valid = 0
        total = 0
        percent_completed = 0
    percent=  ((get_current_processing_line(converted_file) / total_lines)* 100)
    converted_file['percent'] = percent_completed
    edit_file.flush()
    converted_file['file_url'] = upload_media_file(get_file_path(converted_file))
    edit_file.close()
    if valid == total and total!=0:
        update.status = 'complete'
        converted_file['status'] = 'complete'
    elif valid == 0:
        update.status = 'uploaded'
        converted_file['status'] = 'invalidated'
    else:
        update.status = 'partially_complete'
        converted_file['status'] = 'partially_complete'
    

    set_processed_percent(percent_completed, params)
    try:
        os.remove(get_original_file_path(converted_file))
        os.remove(get_file_path(converted_file))
    except:
        return

def create_fcl_freight_freight_rate(
    params, converted_file,  rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
):
    from services.fcl_freight_rate.fcl_celery_worker import create_fcl_freight_rate_delay, celery_extend_create_fcl_freight_rate_data
    keys_to_extract = ['container_size', 'container_type', 'commodity', 'validity_start', 'validity_end', 'schedule_type', 'payment_term', 'rate_type']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    object['validity_start'] = convert_date_format(object.get('validity_start'))
    object['validity_end'] = convert_date_format(object.get('validity_end'))
    for port in [
        "origin_port",
        "origin_main_port",
        "destination_port",
        "destination_main_port",
    ]:
        if rows[0][port]:
            object[f"{str(port)}_id"] = get_port_id(rows[0][port])
    if rows[0]["shipping_line"]:
        object["shipping_line_id"] = get_shipping_line_id(rows[0].get("shipping_line"))
    object["line_items"] = []
    for t in rows:
        if t.get('code') and t.get('price'):
            line_item = {
            'code': t.get('code'),
            'unit': t.get('unit'),
            'price': parse_numeric(t.get('price')),
            'market_price': parse_numeric(t.get('market_price')),
            'currency': t.get('currency'),
            'remarks': [t.get('remark1'), t.get('remark2'), t.get('remark3')] if any([t.get('remark1'), t.get('remark2'), t.get('remark3')]) else None,
            'slabs': []
            }
            object["line_items"].append(line_item)
        elif t.get('weight_free_limit') or t.get('weight_lower_limit'):
            if 'weight_limit' not in object:
                object['weight_limit'] = {}
            if not object['weight_limit'].get('free_limit') and t.get('weight_free_limit'):
                object['weight_limit']['free_limit'] = parse_numeric(t.get('weight_free_limit'))
            if 'slabs' not in object.get('weight_limit'):
                object['weight_limit']['slabs'] = []
            if t.get('weight_lower_limit'):
                if t.get('weight_upper_limit') and t.get('weight_limit_price'):
                    weight_slab = {
                        'lower_limit': parse_numeric(t.get('weight_lower_limit')),
                        'upper_limit': parse_numeric(t.get('weight_upper_limit')),
                        'price': parse_numeric(t.get('weight_limit_price')),
                        'currency': t.get('weight_limit_currency')
                    }
                else:
                    weight_slab = {
                        'lower_limit': parse_numeric(t.get('weight_lower_limit')),
                        'currency': t.get('weight_limit_currency')
                    }
                object['weight_limit']['slabs'].append(weight_slab)


        elif t.get('destination_detention_free_limit') or t.get('destination_detention_lower_limit'):
            if 'destination_local' not in object:
                object['destination_local'] = {'detention': {}}
            if not object['destination_local']['detention'].get('free_limit') and t.get('destination_detention_free_limit'):
                object['destination_local']['detention']['free_limit'] = parse_numeric(t.get('destination_detention_free_limit'))
            if 'slabs' not in object['destination_local']['detention']:
                object['destination_local']['detention']['slabs'] = []
            if t.get('destination_detention_lower_limit'):
                if t.get('destination_detention_price') and t.get('destination_detention_upper_limit'):
                    slab = {
                        'lower_limit': parse_numeric(t.get('destination_detention_lower_limit')),
                        'upper_limit': parse_numeric(t.get('destination_detention_upper_limit')),
                        'price': parse_numeric(t.get('destination_detention_price')),
                        'currency': t.get('destination_detention_currency')
                    }
                else:
                    slab = {
                        'lower_limit': parse_numeric(t.get('destination_detention_lower_limit')),
                        'currency': t.get('destination_detention_currency')
                    }
                object['destination_local']['detention']['slabs'].append(slab)
    object["rate_sheet_id"] = params['rate_sheet_id']
    object["performed_by_id"] = created_by_id
    if params['service_provider_id']:
        object["service_provider_id"] = params['service_provider_id']
    object["procured_by_id"] = procured_by_id
    object["sourced_by_id"] = sourced_by_id
    object["cogo_entity_id"] = params.get('cogo_entity_id')
    object["source"] = "rate_sheet"
    object["is_extended"] = False
    for line_items in object['line_items']:
        if line_items['price']:
            line_items['price'] = parse_numeric(line_items['price'])
    request_params = object
    if 'extend_rates' in rows[0]:
        request_params["is_extended"] = True
        
    if object['line_items'] and object.get('rate_type') == 'cogo_assured':
        price_params = {'price': object['line_items'][0].get('price'), 'currency': object['line_items'][0].get('currency')}
        response = get_suggested_cogo_assured_fcl_freight_rates(price_params)
        object['validities'] = response['data'].get('validities')

    validation = write_fcl_freight_freight_object(request_params, csv_writer, params, converted_file, last_row)
    if validation.get('valid'):
        object['rate_sheet_validation'] = True
        create_fcl_freight_rate_delay.apply_async(kwargs={'request':object},queue='fcl_freight_rate')
        if rows[0].get('extend_rates'):
            request_params['extend_rates'] = True
            celery_extend_create_fcl_freight_rate_data.apply_async(kwargs={'request':object},queue='fcl_freight_rate')
    else:
        print(validation.get('error'))
