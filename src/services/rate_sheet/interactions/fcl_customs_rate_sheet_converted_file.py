import os, csv
from services.rate_sheet.interactions.validate_fcl_customs_object import validate_fcl_customs_object
from services.rate_sheet.helpers import *
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from fastapi.encoders import jsonable_encoder
from services.rate_sheet.interactions.upload_file import upload_media_file


def process_fcl_customs_customs(params, converted_file, update):
    valid_headers = ['location', 'trade_type', 'container_size', 'container_type', 'commodity', 'line_item_type', 'code', 'unit', 'price', 'market_price', 'currency', 'remark1', 'remark2', 'remark3']
    total_lines = 0
    original_path = get_original_file_path(converted_file)
    invalidated = False
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

    edit_file = open(get_file_path(converted_file), 'w')
    with open(original_path, encoding='iso-8859-1') as file:
        csv_writer = csv.writer(edit_file)
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        if last_line == 0:
            csv_writer.writerow(headers)
        
        input_file = csv.DictReader(open(original_path))
        headers = input_file.fieldnames
        if len(set(valid_headers) & set(headers)) != len(valid_headers):
            error_file = ['invalid header']
            csv_writer.writerow(error_file)
            invalidated = True
        for row in input_file:
            if invalidated:
                break
            index += 1
            for k, v in row.items():
                if v == '':
                    row[k] = None
            row = row
            last_line = get_current_processing_line(converted_file)
            present_field = ['location', 'trade_type', 'container_size', 'container_type', 'line_item_type', 'code', 'unit', 'price', 'currency']
            if valid_hash(row, present_field, None):
                if rows:
                    create_fcl_customs_rate(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, ''
                    )
                    set_current_processing_line(index, converted_file)
                rows = [row]
            elif rows and valid_hash(row, ['line_item_type', 'code', 'unit', 'price', 'currency'], ['location', 'trade_type', 'container_size', 'container_type', 'commodity', 'rate_type']):
                rows.append(row)
            if not rows:
                return
        if not invalidated:
            create_fcl_customs_rate(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, '')
        set_current_processing_line(total_lines, converted_file)
    try:
        valid = converted_file.get('valid_rates_count')
        total = converted_file.get('rates_count')
        percent_completed = (valid / total) * 100
    except:
        valid = 0
        total = 0
        percent_completed = 0
    
    if valid == total and total!=0:
        update.status = 'complete'
        converted_file['status'] = 'complete'
    elif valid == 0:
        update.status = 'uploaded'
        converted_file['status'] = 'invalidated'
    else:
        update.status = 'partially_complete'
        converted_file['status'] = 'partially_complete'
    converted_file['file_url'] = upload_media_file(get_file_path(converted_file))
    set_processed_percent(percent_completed, params)
    try:
        os.remove(get_original_file_path(converted_file))
        os.remove(get_file_path(converted_file))
    except:
        return
    return

def create_fcl_customs_rate(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row):
    from celery_worker import create_fcl_customs_rate_delay
    keys_to_extract = ['trade_type', 'container_size', 'container_type', 'commodity','rate_type']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    object['location_id'] = get_port_id(rows[0]['location'])
    object['customs_line_items'] = []
    object['cfs_line_items'] = []
    for t in rows:
        line_item = {
            'code': t.get('code'),
            'unit': t.get('unit'),
            'price': parse_numeric(t.get('price')),
            'market_price': parse_numeric(t.get('market_price')),
            'currency': t.get('currency'),
            'remarks': [t.get('remark1'), t.get('remark2'), t.get('remark3')] if any([t.get('remark1'), t.get('remark2'), t.get('remark3')]) else None,
            'slabs': []
        }
        line_item['location_id'] = get_port_id(t.get('location'))
        if t['line_item_type'] == 'customs_clearance':
            object['customs_line_items'].append(line_item)
        else:
            object['cfs_line_items'].append(line_item)
    object["rate_sheet_id"] = params['rate_sheet_id']
    object["performed_by_id"] = created_by_id
    object["service_provider_id"] = params['service_provider_id']
    object["procured_by_id"] = procured_by_id
    object["sourced_by_id"] = sourced_by_id
    object["source"] = "rate_sheet"
    request_params = object
    validation = write_fcl_customs_customs_object(request_params, csv_writer, params, converted_file, last_row)

    if validation.get('valid'):
        object['rate_sheet_validation'] = True
        create_fcl_customs_rate_delay.apply_async(kwargs={'request':request_params},queue='fcl_freight_rate')
    else:
        print(validation.get('error'))
    return validation

def write_fcl_customs_customs_object(rows, csv, params, converted_file, last_row):
    object_validity = validate_fcl_customs_object(converted_file.get('module'), rows)
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