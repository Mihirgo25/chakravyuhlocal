from services.rate_sheet.interactions.fcl_rate_sheet_converted_file import *
from services.rate_sheet.interactions.validate_fcl_cfs_object import validate_fcl_cfs_object
from configs.fcl_cfs_rate_constants import FREE_DAYS_TYPES

def process_fcl_cfs_cfs(params, converted_file, update):
    valid_headers = ['location', 'trade_type', 'container_size', 'container_type', 'commodity', 'code', 'unit', 'price', 'market_price','currency', 'cargo_handling_type', 'weight_slab_lower_limit', 'weight_slab_upper_limit', 'weight_slab_price', 'weight_slab_currency', 'free_days_type', 'free_days_limit', 'free_days_lower_limit', 'free_days_upper_limit', 'free_days_price', 'free_days_currency', 'remark1', 'remark2', 'remark3']
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

        if len(set(valid_headers) & set(headers)) != len(valid_headers):
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
            row = row
            present_field = ['location', 'trade_type', 'container_size', 'container_type', 'code', 'unit', 'price', 'currency', 'cargo_handling_type']

            is_main_rate_row = False
            if row['location']:
                is_main_rate_row = True
            if valid_hash(row, present_field, None):
                if rows:
                    last_row = list(row.values())
                    if is_previous_rate_valid:
                        create_fcl_cfs_rate(
                            params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row
                        )
                    else:
                        is_previous_rate_valid = True
                    set_current_processing_line(index-1, converted_file)
                    percent = ((get_current_processing_line(converted_file) / total_lines)* 100)
                    set_processed_percent(percent, params)
                else:
                    list_opt = list(row.values())
                    csv_writer.writerow(list_opt)
                rows = [row]
            elif rows and (valid_hash(
                row, 
                ['code', 'unit', 'price', 'currency'], 
                [
                    'location', 
                    'trade_type', 
                    'container_size', 
                    'container_type', 
                    'commodity', 
                    'cargo_handling_type', 
                    'weight_slab_lower_limit', 
                    'weight_slab_upper_limit', 
                    'weight_slab_price', 
                    'weight_slab_currency', 
                    'free_days_type', 
                    'free_days_limit', 
                    'free_days_lower_limit', 
                    'free_days_upper_limit', 
                    'free_days_price', 
                    'free_days_currency'
                ]) or
                valid_hash(
                row, 
                [
                    'weight_slab_lower_limit', 
                    'weight_slab_upper_limit', 
                    'weight_slab_price', 
                    'weight_slab_currency'
                ], 
                [
                    'code', 
                    'unit', 
                    'price', 
                    'currency', 
                    'location', 
                    'trade_type', 
                    'container_size', 
                    'container_type', 
                    'commodity', 
                    'cargo_handling_type', 
                    'free_days_type', 
                    'free_days_limit', 
                    'free_days_lower_limit', 
                    'free_days_upper_limit', 
                    'free_days_price', 
                    'free_days_currency'
                ]) or
                valid_hash(
                row, 
                ['free_days_type', 'free_days_limit'], 
                [
                    'code', 
                    'unit', 
                    'price', 
                    'currency', 
                    'location', 
                    'trade_type', 
                    'container_size', 
                    'container_type', 
                    'commodity', 
                    'cargo_handling_type', 
                    'weight_slab_lower_limit', 
                    'weight_slab_upper_limit', 
                    'weight_slab_price', 
                    'weight_slab_currency', 
                    'free_days_lower_limit', 
                    'free_days_upper_limit', 
                    'free_days_price', 
                    'free_days_currency'
                ]) or
                valid_hash(
                    row, 
                    [
                        'free_days_lower_limit', 
                        'free_days_upper_limit', 
                        'free_days_price', 
                        'free_days_currency'
                    ], 
                    [
                        'code', 
                        'unit', 
                        'price', 
                        'currency', 
                        'location', 
                        'trade_type', 
                        'container_size', 
                        'container_type', 
                        'commodity', 
                        'cargo_handling_type', 
                        'weight_slab_lower_limit', 
                        'weight_slab_upper_limit', 
                        'weight_slab_price', 
                        'weight_slab_currency', 
                        'free_days_type', 
                        'free_days_limit'
                    ]
                )):
                rows.append(row)
                list_opt = list(row.values())
                csv_writer.writerow(list_opt)
            else:
                list_opt = []
                if rows and is_previous_rate_valid and is_main_rate_row:
                    last_row = list(row.values())
                    create_fcl_cfs_rate(
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
        create_fcl_cfs_rate(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, '')
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

def create_fcl_cfs_rate(params, converted_file, rows, created_by_id, procured_by_id, sourced_by_id, csv_writer, last_row):
    from services.fcl_cfs_rate.fcl_cfs_celery_worker import create_fcl_cfs_rate_delay
    keys_to_extract = ['trade_type', 'container_size', 'container_type', 'commodity','cargo_handling_type']
    object = dict(filter(lambda item: item[0] in keys_to_extract, rows[0].items()))
    object['location_id'] = get_port_id(rows[0]['location'])
    object['line_items'] = []
    object['free_days'] = []
    object['accuracy'] = 100
    for t in rows:
        if t.get('code'):
            line_item = {
                'code': t.get('code'),
                'unit': t.get('unit'),
                'price': parse_numeric(t.get('price')),
                'market_price': parse_numeric(t.get('market_price')),
                'currency': t.get('currency'),
                'remarks': [t.get('remark1'), t.get('remark2'), t.get('remark3')] if any([t.get('remark1'), t.get('remark2'), t.get('remark3')]) else None,
                'slabs': []
            }
            object['line_items'].append(line_item)
        if t.get('weight_slab_lower_limit'):
            if not object['line_items'][-1].get('weight_slabs'):
                object['line_items'][-1]['weight_slabs'] = []
            weight_slab = {
                'lower_limit': t.get('weight_slab_lower_limit'),
                'upper_limit': t.get('weight_slab_upper_limit'),
                'price': t.get('weight_slab_price'),
                'currency': t.get('weight_slab_currency')
            }
            object['line_items'][-1]['weight_slabs'].append(weight_slab)
        if t.get('free_days_type'):
            free_days_type = ''
            for free_day in FREE_DAYS_TYPES:
                if free_day['name'].lower() == t.get('free_days_type').lower():
                    free_days_type = free_day['type']
            free_day = {
                'free_days_type': free_days_type,
                'free_limit': t.get('free_days_limit')
            }
            object['free_days'].append(free_day)
        if t.get('free_days_lower_limit'):
            if not object['free_days'][-1].get('slabs'):
                object['free_days'][-1]['slabs'] = []
            slab = {
                'lower_limit': t.get('free_days_lower_limit'),
                'upper_limit': t.get('free_days_upper_limit'),
                'price': t.get('free_days_price'),
                'currency': t.get('free_days_currency')
            }
            object['free_days'][-1]['slabs'].append(slab)

    object["rate_sheet_id"] = params['rate_sheet_id']
    object["performed_by_id"] = created_by_id
    object["service_provider_id"] = params['service_provider_id']
    object["procured_by_id"] = procured_by_id
    object["sourced_by_id"] = sourced_by_id
    object["source"] = "rate_sheet"
    request_params = object
    validation = write_fcl_cfs_cfs_object(request_params, csv_writer, params, converted_file, last_row)
    
    if validation.get('valid'):
        object['rate_sheet_validation'] = True
        create_fcl_cfs_rate_delay.apply_async(kwargs={'request':request_params},queue='fcl_freight_rate')
    else:
        print(validation.get('error'))
    return validation

def write_fcl_cfs_cfs_object(rows, csv, params, converted_file, last_row):
    object_validity = validate_fcl_cfs_object(converted_file.get('module'), rows)
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