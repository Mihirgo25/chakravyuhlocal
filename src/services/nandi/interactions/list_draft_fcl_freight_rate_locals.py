from services.nandi.models.draft_fcl_freight_rate_local import DraftFclFreightRateLocal
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
import json
from libs.json_encoder import json_encoder
from peewee import fn, SQL

possible_direct_filters = ["id", "commodity", "container_size", "container_type", "port_id", "shipping_line_id", "trade_type", "rate_id", "source", "status", "shipment_serial_id"]
possible_indirect_filters = []

def list_draft_fcl_freight_rate_locals(filters = {}, page_limit = 10, page = 1, sort_by = 'updated_at', sort_type = 'desc', is_stats_required = True):
    query = get_query(sort_by, sort_type)

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

            direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

            query = get_filters(direct_filters, query, DraftFclFreightRateLocal)

    stats = get_stats(filters, is_stats_required) or {}
    query = query.paginate(page, page_limit)
    data = get_data(query)
    return { 'list': json_encoder(data) } | (stats)

def get_query(sort_by, sort_type):
    query = DraftFclFreightRateLocal.select().order_by(eval("DraftFclFreightRateLocal.{}.{}()".format(sort_by, sort_type)))
    return query

def get_data(query):
    sid_wise_data = {}
    for row in query.dicts():
        row['invoice_urls'] = []
        if not sid_wise_data.get(row.get('shipment_serial_id')):
            sid_wise_data[row['shipment_serial_id']] = row
            sid_wise_data[row['shipment_serial_id']]['invoice_urls'].append(row['invoice_url'])
            continue
        sid_wise_data[row['shipment_serial_id']]['data']['line_items'].extend(row['data']['line_items'])
        sid_wise_data[row['shipment_serial_id']]['invoice_urls'].append(row['invoice_url'])
        sid_wise_data[row['shipment_serial_id']]['invoice_urls'] = list(set(sid_wise_data[row['shipment_serial_id']]['invoice_urls']))
    data = list(sid_wise_data.values())
    return data

def get_stats(filters, is_stats_required):
    if not is_stats_required:
        return {}
    
    query = DraftFclFreightRateLocal.select()

    if filters:
        if 'status' in filters:
            del filters['status']
    
        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)
  
        query = get_filters(direct_filters, query, DraftFclFreightRateLocal)

    query = (query.select(
        fn.count(DraftFclFreightRateLocal.id).over().alias('get_total'),
        fn.count(DraftFclFreightRateLocal.id).filter(DraftFclFreightRateLocal.status == 'pending').over().alias('get_status_count_pending')

         )
    ).limit(1)

    result = query.execute()
    if len(result)>0:
        result =result[0]
        stats = {
        'total': result.get_total,
        'pending': result.get_status_count_pending
        }
    else:
        stats ={}
    return { 'stats': stats }