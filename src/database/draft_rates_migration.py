from services.nandi.models.draft_fcl_freight_rate_local import DraftFclFreightRateLocal
from services.nandi.models.draft_fcl_freight_rate_local_audit import DraftFclFreightRateLocalAudit
import pandas as pd
from database.rails_db import get_user
import json
from datetime import datetime

def draft_rates_migration():
    draft_rates_csv = pd.read_csv('/Users/shreyasnakshatram/Desktop/chakravyuh/src/database/draft_rates_locals.csv')
    draft_rates_csv.sort_values(['shipment_serial_id','invoice_date'], ascending= [False, False], inplace = True)
    draft_rates_csv = draft_rates_csv.where(pd.notnull(draft_rates_csv), None)

    for row in range(len(draft_rates_csv)):
        draft_rates_csv['data'][row] = draft_rates_csv['data'][row].replace('null','None')
        draft_rates_csv['data'][row] = eval(draft_rates_csv['data'][row])
        try:
            draft_rates_csv['main_port'][row] = json.loads(draft_rates_csv['main_port'][row])
        except:
            draft_rates_csv['main_port'][row] = None
        draft_rates_csv['port'][row] = json.loads(draft_rates_csv['port'][row])
        draft_rates_csv['shipping_line'][row] = json.loads(draft_rates_csv['shipping_line'][row])
    draft_rates_csv.reset_index(drop = True, inplace = True)
    dict_new = draft_rates_csv.to_dict(orient = 'records')

    sid_wise_data = {}
    for row in dict_new:
        row['invoice_date'] = datetime.strptime(row['invoice_date'], '%Y-%m-%d').date()
        row['invoice_urls'] = []
        row['invoice_dates'] = []
        row['ids'] = []
        key = str(row.get('shipment_serial_id')) + str(row.get('status'))
        if not sid_wise_data.get(key):
            sid_wise_data[key] = row
            sid_wise_data[key]['invoice_urls'].append(row['invoice_url'])
            sid_wise_data[key]['invoice_dates'].append(row['invoice_date'])
            sid_wise_data[key]['invoice_url'] = sid_wise_data[key]['invoice_urls']
            sid_wise_data[key]['invoice_date'] = sid_wise_data[key]['invoice_dates']
            sid_wise_data[key]['ids'].append(row['id'])
            continue
        sid_wise_data[key]['data']['line_items'].extend(row['data']['line_items'])
        sid_wise_data[key]['invoice_urls'].append(row['invoice_url'])
        sid_wise_data[key]['invoice_dates'].append(row['invoice_date'])
        sid_wise_data[key]['ids'].append(row['id'])
        sid_wise_data[key]['invoice_url'] = list(set(sid_wise_data[key]['invoice_urls']))
        sid_wise_data[key]['invoice_date'] = list(set(sid_wise_data[key]['invoice_dates']))
        # sid_wise_data[key]['invoice_url'] = sid_wise_data[key]['invoice_urls']
        sid_wise_data[key]['data']['line_items'] = remove_duplicate_line_items(sid_wise_data[key]['data']['line_items'])
        break
    data = list(sid_wise_data.values())
    i = 0
    for row in data:
        i += 1
        print('going {}'.format(i))
        DraftFclFreightRateLocal.create(**row)
        break
        # object.save()

def remove_duplicate_line_items(data):
    unique_items = {}
    for item in data:
        unique_items[item["code"]] = item

    unique_data = list(unique_items.values())
    return unique_data

def set_performed_by_draft_locals():
    audits = DraftFclFreightRateLocalAudit.select(
        DraftFclFreightRateLocalAudit.object_id,
        DraftFclFreightRateLocalAudit.performed_by_id
    ).where(
        DraftFclFreightRateLocalAudit.action_name == 'update'
    ).execute()

    performed_by_dict = {}
    for audit in audits:
        performed_by_dict[audit.object_id] = audit.performed_by_id
    
    draft_rates = DraftFclFreightRateLocal.select().where(
        DraftFclFreightRateLocal.status != 'pending'
    ).execute()

    for rate in draft_rates:
        rate.performed_by_id = performed_by_dict.get(str(rate.id or ''))
        if rate.performed_by_id:
            rate.performed_by = get_user(str(rate.performed_by_id))
        rate.save()