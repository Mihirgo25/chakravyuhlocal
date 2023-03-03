import os, csv
import shutil
import urllib.request
from libs.download_csv import download_file
from services.rate_sheet.models.rate_sheet import RateSheet
import pandas as pd
from rails_client import client
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.extend_create_fcl_freight_rate import extend_create_fcl_freight_rate_data
from database.db_session import rd


# Set up CSV options
csv_options = {
    'encoding': 'iso-8859-1',
    'quotechar': None,
    'skip_blank_lines': True,
    'skipinitialspace': True,
    'skiprows': lambda x: x.startswith(',')  # use regex pattern in the skiprows parameter
}

last_line_hash = 'last_line'
total_line_hash = 'total_line'


def last_line_key(params):
    return f"rate_sheet_converted_file_last_line_{params.id}"

def set_last_line(last_line):
    if rd:
        rd.hset(last_line_hash, last_line_key, last_line)

def get_last_line():
    if rd:
        cached_response = rd.hget(last_line_hash, last_line_key)
        return cached_response

def delete_last_line(last_line_hash):
    if rd:
        rd.delete(last_line_hash, last_line_key)

def total_line_keys(params):
    return f"rate_sheet_converted_file_total_lines_{params.id}"

def set_total_line(total_line):
    if rd:
        rd.hset(total_line_hash, total_line_keys, total_line)

def get_total_line():
    if rd:
        cached_response = rd.hget(total_line_hash, total_line_keys)
        return cached_response

def delete_total_line(total_line_hash):
    if rd:
        rd.delete(total_line_hash, total_line_keys)

def get_port_id(port_code):
    port_id = client.ruby.list_locations({'filters': { 'type': 'seaport', 'port_code': port_code, 'status': 'active'}, 'fields': ['id'] })['list'][0]['id']
    return port_id

def get_airport_id(port_code, country_code):
    airport_id = client.ruby.list_locations({'filters': { 'type': 'airport', 'port_code': port_code, 'status': 'active', 'country_code': country_code }, 'fields': ['id'] })['list'][0]['id']
    return airport_id

def get_shipping_line_id(shipping_line_name):
    shipping_line_id =  client.ruby.list_operators({'filters': {'operator_type': 'shipping_line','short_name': shipping_line_name, 'status':'active'}})['list'][0]
    return shipping_line_id

def get_airline_id(params):
    airline_id = client.ruby.list_operators({'filters':{'id': params.origin_location_id}})['list'][0]
    return airline_id

def convert_date_format(date):
    return date.strftime("%D:%M:%Y")

def process_fcl_freight_freight(params):
    total_lines = 0
    print('test')
    print(get_original_file_path)
    for _ in pd.read_csv(get_original_file_path, header=0, **csv_options):
        total_lines += 1
    set_total_line(total_lines)
    last_line = get_last_line
    rows = []
    rate_sheet = RateSheet.find(params.rate_sheet_id)
    created_by_id = rate_sheet.created_by_id
    procured_by_id = rate_sheet.procured_by_id
    sourced_by_id = rate_sheet.sourced_by_id
    index = -1
    df = pd.read_csv(get_original_file_path, header=0, **csv_options)
    for idx, row in df.iterrows():
        index+=1
        row = row
        if index < last_line:
            continue
        present_field = []
        blank_field = []
        if valid_hash(row, present_field, blank_field):
            if rows:
                create_fcl_freight_freight_rate(rows, created_by_id, procured_by_id, sourced_by_id)
                set_last_line(index)
                rate_sheet.set_processed_percent = (((params.file_index * 1.0) / rate_sheet.converted_files.count) * ((get_last_line * 1.0) / get_total_line)) * 100
            rows = [row]
        elif valid_hash('row', ['code', 'unit', 'price', 'currency'], ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'validity_start', 'validity_end', 'weight_free_limit', 'weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency', 'destination_detention_free_limit', 'destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency']) or  valid_hash('row', ['weight_free_limit'], ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'code', 'unit', 'price', 'currency', 'validity_start', 'validity_end', 'weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency', 'destination_detention_free_limit', 'destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency']) or valid_hash('row', ['weight_free_limit', 'weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency'], ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'code', 'unit', 'price', 'currency', 'validity_start', 'validity_end', 'destination_detention_free_limit', 'destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency']) or valid_hash('row', ['weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency'], ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'code', 'unit', 'price', 'currency', 'validity_start', 'validity_end', 'weight_free_limit', 'destination_detention_free_limit', 'destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency']) or valid_hash('row', ['destination_detention_free_limit'], ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'code', 'unit', 'price', 'currency', 'validity_start', 'validity_end', 'weight_free_limit', 'weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency', 'destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency']) or valid_hash('row', ['destination_detention_free_limit', 'destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency'], ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'code', 'unit', 'price', 'currency', 'validity_start', 'validity_end', 'weight_free_limit', 'weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency']) or valid_hash('row', ['destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency'], ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port', 'container_size', 'container_type', 'commodity', 'shipping_line', 'code', 'unit', 'price', 'currency', 'validity_start', 'validity_end', 'weight_free_limit', 'weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency', 'destination_detention_free_limit']):
            rows.append(row)

    if not rows:
        return

    create_fcl_freight_freight_rate(rows, created_by_id, procured_by_id, sourced_by_id)
    set_last_line(total_lines)
    rate_sheet.set_processed_percent = (((params.file_index * 1.0) / rate_sheet.converted_files.count) * ((get_last_line * 1.0) / get_total_line)) * 100




def create_fcl_freight_freight_rate(params, rows, created_by_id, procured_by_id, sourced_by_id):
    # object = rows[0].slice(:container_size, :container_type, :commodity, :validity_start, :validity_end, :schedule_type, :payment_term)
    object = rows[0]
    object['validity_start'] = convert_date_format( object['validity_start'])
    object['validity_end'] = convert_date_format( object['validity_end'])
    for port in ['origin_port', 'origin_main_port', 'destination_port', 'destination_main_port']:
        object[f"{str(port)}_id"] = get_port_id(rows[0][port])
    object['shipping_line_id'] = get_shipping_line_id(rows[0]['shipping_line'])
    object['line_items'] = []
    # incomplete rows
    for t in rows:
        if 'code' in t:
            line_item = t
            line_item['remark'] = list(filter(None,[t['remark1'], t['remark2'], t['remark3']]))
            line_item['slabs'] = []
            line_item['line_items'].append(line_item)
        elif 'weight_free_limit' in t or 'weight_lower_limit' in t:
            object['weight_limit'] =  object['weight_limit'] or {}
            object['weight_limit']['free_limit'] = object['weight_limit']['free_limit'] or t['weight_free_limit']
            object['weight_limit']['slabs'] = object['weight_limit']['slabs'] or []
            keys_to_extract = ['weight_lower_limit', 'weight_upper_limit', 'weight_limit_price', 'weight_limit_currency']
            weight_slab = dict(filter(lambda item: item[0] in keys_to_extract, t.items()))
            del weight_slab['weight_lower_limit']
            weight_slab['lower_limit'] = weight_slab
            del weight_slab['weight_upper_limit']
            weight_slab['upper_limit'] = weight_slab
            del weight_slab['weight_limit_price']
            weight_slab['price'] = weight_slab
            del weight_slab['weight_limit_currency']
            weight_slab['currency'] = weight_slab

            if weight_slab['lower_limit'] is not None:
                object['weight_limit']['slabs'].append(weight_slab)

        elif t['destination_detention_free_limit'] is not None or t['destination_detention_lower_limit'] is not None:
            object['destination_local'] = {'detention' : {}}
            object['destination_local']['detention']['free_limit'] =  object['destination_local']['detention']['free_limit'] or t['destination_detention_free_limit']
            object['destination_local']['detention']['slabs'] = object['destination_local']['detention']['slabs'] or []
            keys_to_extract = ['destination_detention_lower_limit', 'destination_detention_upper_limit', 'destination_detention_price', 'destination_detention_currency']
            slab = dict(filter(lambda item: item[0] in keys_to_extract, t.items()))
            del slab['destination_detention_lower_limit']
            slab['lower_limit'] = slab
            del slab['destination_detention_upper_limit']
            slab['upper_limit'] = slab
            del slab['destination_detention_price']
            slab['price'] = slab
            del slab['destination_detention_currency']
            slab['currency'] = slab
            if slab['lower_limit'] is not None:
                object['destination_local']['detention']['slabs'].append(slab)
    object['rate_sheet_id'] = params.rate_sheet_id
    object['performed_by_id'] = created_by_id
    object['service_provider_id'] = params.service_provider_id
    object['procured_by_id'] = procured_by_id
    object['sourced_by_id'] = sourced_by_id
    object['cogo_entity_id'] = params.cogo_entity_id
    object['source'] = 'rate_sheet'
    object['is_extended'] = False
    request_params = object
    if rows[0]['extended_rates'] is not None:
        request_params['is_extended'] = True
    create_fcl_freight_rate_data(request_params)
    if rows[0]['extended_rates'] is not None:
        request_params['extend_rates'] = True
        del request_params['is_extended']
        extend_create_fcl_freight_rate_data(request_params)




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
        "service_provider_id": params['service_provider_id']
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
                "slabs": []
            }
            object["data"]["line_items"].append(line_item)
        else:
            slab = {
                "lower_limit": t["lower_limit"],
                "upper_limit": t["upper_limit"],
                "price": t["price"],
                "currency": t["currency"]
            }
            object["data"]["line_items"][-1]["slabs"].append(slab)

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
    return

def create_fcl_freight_rate_weight_limit(params):
    return

def mark_processing(params):
    params.status = 'processing'
    return params

def reset_counters(params):
    return

def delete_temp_data(params):
    return

def get_original_file_path(params):
    os.makedirs('tmp/rate_sheets', exist_ok=True)
    os.path.join('tmp', 'rate_sheets', f"{params.id}_original.csv")

def delete_original_file_path(params):
    try:
        os.remove(get_file_path(params))
    except FileNotFoundError:
        pass

def set_original_file_path(params):
    os.makedirs('tmp/rate_sheets', exist_ok=True)
    urllib.request.urlretrieve(params.file_url, os.path.join('tmp', 'rate_sheets', f"{params.id}_original.csv"))
    return

def get_file_path(params):
    os.makedirs('tmp/rate_sheets', exist_ok=True)
    return os.path.join('tmp', 'rate_sheets', f"{params.id}.csv")

def delete_file_path(params):
    try:
        os.remove(get_file_path(params))
    except FileNotFoundError:
        pass

def get_location_id(q,  country_code = None , service_provider_id = None ):
    pincode_filters =  { 'type': 'pincode', 'postal_code': q, 'status': 'active' }
    if country_code is not None:
        pincode_filters = pincode_filters.merge({ country_code: country_code })
    locations = client.ruby.list_locations({ 'filters': pincode_filters, 'fields': ['id'] })['list']
    if not locations:
        locations = client.ruby.list_locations({ 'filters': { 'type': 'country', 'country_code': q, 'status': 'active' }, 'fields': ['id'] })['list']
    seaport_filters =  { 'type': 'seaport', 'port_code': q, 'status': 'active' }
    if not locations:
        country_filters = {'type': 'country', 'country_code': q, 'status': 'active'}
        if country_code is not None:
            country_filters = {**country_filters, 'country_code': country_code}
        locations = client.ruby.list_locations(filters=country_filters, fields=['id'])['list']
    seaport_filters = {'type': 'seaport', 'port_code': q, 'status': 'active'}
    if country_code is not None:
        seaport_filters = {**seaport_filters, 'country_code': country_code}
    locations = client.ruby.list_locations(filters=seaport_filters, fields=['id'])['list'] if not locations else locations
    airport_filters = {'type': 'airport', 'port_code': q, 'status': 'active'}
    if country_code is not None:
        airport_filters = {**airport_filters, 'country_code': country_code}
    locations = client.ruby.list_locations(filters=airport_filters, fields=['id'])['list'] if not locations else locations
    name_filters = {'name': q, 'status': 'active'}
    if country_code is not None:
        name_filters = {**name_filters, 'country_code': country_code}
    locations = client.ruby.list_locations(filters=name_filters, fields=['id'])['list'] if not locations else locations
    display_name_filters = {'display_name': q, 'status': 'active'}
    if country_code is not None:
        display_name_filters = {**display_name_filters, 'country_code': country_code}
    locations = client.ruby.list_locations(filters=display_name_filters, fields=['id'])['list'] if not locations else locations

    # if not locations:
    #     locations = client.ruby.list_ltl_freight_rate_zones(name=q, service_provider_id=service_provider_id).values_list('id', flat=True)
    #     return locations[0] if locations else None

    return locations[0]['id'] if locations else None


def valid_hash(hash, present_fields = [], blank_fields = []):
    for field in present_fields:
        if not hash[field]:
            return False
    for field in blank_fields:
        if not hash[field]:
            return False
    return True

def get_location(location, type):
    if type == 'port':
        location = client.ruby.list_locations({ 'filters': { 'type': 'seaport', 'port_code': location, 'status': 'active' } })['list'][0]
    else:
        location = client.ruby.list_locations({ 'filters': { 'type': type, 'name': location, 'status': 'active' } })['list'][0]
    return

def get_importer_exporter_id(importer_exporter_name):
    importer_exporter_id = client.ruby.list_organizations({ 'filters': { 'account_type': 'importer_exporter', 'short_name': importer_exporter_name, 'status': 'active' } })['list'][0]
    return importer_exporter_id

def validate_fcl_freight_freight(params):

    return

def write_fcl_freight_freight_object(params):
    return

def validate_fcl_freight_local(params):
    return



def fcl_rate_sheet_converted_file(params):

    # fcl Freight  Module

    validate_fcl_freight_freight(params)

    # write_fcl_freight_local_object(params)

    # create_fcl_freight_freight_rate(params)

    process_fcl_freight_freight(params)

    # Fcl Freight Local Module

    # write_fcl_freight_local_object(params)

    validate_fcl_freight_local(params)

    # create_fcl_freight_rate_local(params)

    process_fcl_freight_local(params)

    # Fcl Freight Free Day Module

    validate_fcl_freight_free_day(params)

    # create_fcl_freight_rate_free_day(params)

    process_fcl_freight_free_day(params)



    params = mark_processing(params)
