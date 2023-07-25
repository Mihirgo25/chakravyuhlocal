from services.rate_sheet.interactions.fcl_rate_sheet_converted_file import *
from services.rate_sheet.interactions.validate_air_customs_object import validate_air_customs_object

def process_air_customs_customs(params, converted_file, update):
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

    edit_file = open(get_file_path(converted_file), 'w')
    with open(original_path, encoding='iso-8859-1') as file:
        csv_writer = csv.writer(edit_file)
        reader = csv.reader(file, skipinitialspace=True, delimiter=',', quotechar=None)
        if last_line == 0:
            csv_writer.writerow(headers)
        
        input_file = csv.DictReader(open(original_path))
        for row in input_file:
            index += 1
            for k, v in row.items():
                if v == '':
                    row[k] = None
            row = row
            last_line = get_current_processing_line(converted_file)
            present_field = ['airport', 'country', 'trade_type', 'code', 'unit', 'price', 'currency']
            if valid_hash(row, present_field, None):
                if rows:
                    create_air_customs_rate(
                        params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, ''
                    )
                    set_current_processing_line(index, converted_file)
                rows = [row]
            elif rows and valid_hash(row, ['code', 'unit', 'price', 'currency'], ['airport', 'country', 'trade_type', 'commodity', 'rate_type']):
                rows.append(row)
            if not rows:
                return
        create_air_customs_rate(
            params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, ''
        )
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

    set_processed_percent(percent_completed, params)
    try:
        os.remove(get_original_file_path(converted_file))
        os.remove(get_file_path(converted_file))
    except:
        return
    return

def create_air_customs_rate(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row):
    from services.air_customs_rate.celery_worker.air_customs_celery import create_air_customs_rate_delay
    keys_to_extract = ['trade_type', 'commodity', 'rate_type']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    object['airport_id'] = get_airport_id(rows[0]['airport'], rows[0]['country'])
    object['line_items'] = []
    object['accuracy'] = 100
    for t in rows:
        line_item = {
            'code': t.get('code'),
            'unit': t.get('unit'),
            'price': parse_numeric(t.get('price')),
            'currency': t.get('currency'),
            'remarks': [t.get('remark1'), t.get('remark2'), t.get('remark3')] if any([t.get('remark1'), t.get('remark2'), t.get('remark3')]) else None,
            'slabs': []
        }
        object['line_items'].append(line_item)

    object["rate_sheet_id"] = params['rate_sheet_id']
    object["performed_by_id"] = created_by_id
    object["service_provider_id"] = params['service_provider_id']
    object["procured_by_id"] = procured_by_id
    object["sourced_by_id"] = sourced_by_id
    object["source"] = "rate_sheet"
    request_params = object
    validation = write_air_customs_customs_object(request_params, csv_writer, params, converted_file, last_row)

    if validation.get('valid'):
        object['rate_sheet_validation'] = True
        create_air_customs_rate_delay.apply_async(kwargs={'request':request_params},queue='fcl_freight_rate')
    else:
        print(validation.get('error'))
    return validation

def write_air_customs_customs_object(rows, csv, params, converted_file, last_row):
    object_validity = validate_air_customs_object(converted_file.get('module'), rows)
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