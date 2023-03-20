from services.rate_sheet.models.rate_sheet import RateSheet
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from libs.get_filters import get_filters
from fastapi.encoders import jsonable_encoder
import services.rate_sheet.interactions.list_rate_sheets as list_rate_sheet
import json, uuid, math
import concurrent.futures
from rails_client import client

from peewee import *
from database.db_session import rd
from services.rate_sheet.interactions.fcl_rate_sheet_converted_file import get_total_line, get_last_line
from datetime import datetime

POSSIBLE_DIRECT_FILTERS = ['id', 'agent_id', 'service_provider_id', 'status', 'service_name', 'serial_id', 'cogo_entity_id']
POSSIBLE_INDIRECT_FILTERS = ['performed_by_id', 'partner_id']

processed_percent_hash = "total_line"



def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def apply_direct_filters(query, filters):
    query = get_filters(filters, query, RateSheet, "")
    return query


def apply_indirect_filters(query, filters):
    for key, val in filters.items():
        query = getattr(list_rate_sheet, "apply_{}_filter".format(key))(
            query, val
        )
    return query

def apply_partner_id_filter(query, val):
    cogo_entity_id = val
    query = query.where(RateSheet.cogo_entity_id << [cogo_entity_id, None])
    return query


def apply_performed_by_id_filter(query, val):
    query = query.join(RateSheetAudit).where(RateSheetAudit.performed_by_id == val)
    return query



def get_direct_indirect_filters(filters):
    direct_filters = {}
    indirect_filters = {}
    for key, val in filters.items():
        if key in POSSIBLE_DIRECT_FILTERS:
            direct_filters[key] = val
        if key in POSSIBLE_INDIRECT_FILTERS:
            indirect_filters[key] = val
    for type in [
        "id",
        "continent_id",
        "trade_id",
        "country_id",
        "region_id",
        "city_id",
        "cluster_id",
        "pincode_id",
        "seaport_id",
        "airport_id",
    ]:
        if type in direct_filters:
            if isinstance(direct_filters[type], str):
                if not is_valid_uuid(direct_filters[type]):
                    del direct_filters[type]
            elif isinstance(direct_filters[type], list):
                for key in direct_filters[type]:
                    if not is_valid_uuid(key):
                        direct_filters[type].remove(key)
    return direct_filters, indirect_filters



def apply_pagination(query, page, page_limit):
    offset = (page - 1) * page_limit
    total_count = query.count()
    query = query.offset(offset).limit(page_limit)
    return query, total_count

def processed_percent_key(id):
  return f"rate_sheet_converted_file_processed_percent_{id}"

def set_processed_percent(processed_percent, id):
    if rd:
        rd.hset(processed_percent_hash, processed_percent_key(id), processed_percent)
        rd.expire(processed_percent_key(id), 864000)
    return

def get_processed_percent(id):
    if rd:
        try:
            cached_response = rd.hget(processed_percent_hash, processed_percent_key(id))
            return int(cached_response)
        except:
            return 0
    return

def delete_processed_percent(id):
    if rd:
        rd.delete(processed_percent_hash, processed_percent_key(id))



def detail(data):
    for d in data:
        d['processed_percent'] = get_processed_percent(d['id'])
        d['converted_files'] = []
        for converted_file in data.get('converted_file'):
            for converted_file_json in converted_file:
                converted_file_json['total_lines'] = get_total_line(converted_file)
                converted_file_json['last_line'] = get_last_line(converted_file)
            d['converted_files'].append(converted_file)
    return data


def add_service_objects(data):
    if len(data) == 0:
        return data
    objects_organizations_hash = {}
    objects_organizations = {
        "filters": {"id": []},
        "fields": ['id', 'business_name', 'short_name', 'logo_url']
    }
    objects_user_hash = {}
    objects_user = {
        "filters": {"id": []},
        "fields": ['id', 'name', 'email']
    }
    org_ids = []
    user_ids = []
    for cluster in data:
        try:
            org_id = cluster.get('service_provider_id')
            if org_id:
                org_ids.append(org_id)
            user_id = [cluster.get('procured_by_id'), cluster.get('sourced_by_id'), cluster.get('performed_by_id')]
            if user_id:
                user_ids+=user_id
        except:
            continue

    if len(org_ids):
        objects_organizations['filters']['id'] = org_ids
        list_organizations = client.ruby.list_organizations(
            objects_organizations
        )
        for org in list_organizations['list']:
            objects_organizations_hash[org['id']] =org['business_name']

    if len(user_ids):
        objects_user['filters']['id'] = user_ids
        list_user = client.ruby.list_users(objects_user)
        for user_obj in list_user['list']:
            objects_user_hash[user_obj['id']] =user_obj['business_name']

    for object in data:
        object['service_provider'] = objects_organizations_hash.get('organization')
        # if cluster['organization_id'] in objects_organizations_hash:
        #     cluster['organization_name'] = objects_organizations_hash[cluster['organization_id']]
        # if cluster['user_id'] in objects_user_hash:
        #     cluster['user_name'] = objects_user_hash[cluster['user_id']]

    return data


def get_final_data(query):
    data = list(query.dicts())
    final_data = jsonable_encoder(data)
    final_data = detail(final_data)
    audit_ids = []
    audit_ids = [data['id'] for data in final_data]
    rate_sheet_audits = RateSheetAudit.select().where(RateSheetAudit.object_id << audit_ids)

    for object in final_data:
        # assumption here
        rates_count_sum=0
        for obj in object.get('converted_files'):
            rates_count_sum+=obj.get('rates_count')
        if 'converted_files' in object:
            object['rates_count'] = rates_count_sum
        rate_sheet_audit = rate_sheet_audits.where(RateSheetAudit.object_id == object['id']).order_by(RateSheetAudit.created_at.desc()).limit(1).dicts().get()
        object['sourced_by_id'] = rate_sheet_audit.get('sourced_by_id')
        object['procured_by_id'] = rate_sheet_audit.get('procured_by_id')
        object['performed_by_id'] = rate_sheet_audit.get('performed_by_id')

    final_data = add_service_objects(final_data)


    return final_data

def add_pagination_data(
    response, page, total_count, page_limit, final_data, pagination_data_required
):
    if pagination_data_required:
        response["page"] = page
        response["total"] = math.ceil(total_count / page_limit)
        response["total_count"] = total_count
        response["page_limit"] = page_limit
    response["success"] = True
    response["list"] = final_data
    return response


def get_data(query):
    # perform some computation or database query
    # ...
    return query

def get_pagination_data(query):
    # perform some computation or database query
    # ...
    return query

def list_rate_sheets(filters, stats_required, page, page_limit, sort_by, sort_type, pagination_data_required):
    response = {"success": False, "status_code": 200}

    if filters is None:
        filters = {}
    else:
        filters = json.loads(filters)

    query = RateSheet.select()
    if len(filters) != 0:
        direct_filters, indirect_filters = get_direct_indirect_filters(filters)
        query = apply_direct_filters(query, direct_filters)
        query = apply_indirect_filters(
            query, indirect_filters
        )
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # submit each method to the executor and store the resulting futures
        data_future = executor.submit(get_final_data, query)
        pagination_data_future = executor.submit(get_pagination_data, query)

    data = data_future.result()
    pagination_data = pagination_data_future.result()
    # with concurrent.futures.ThreadPoolExecutor(max_workers = len(detention_and_demurrage_free_days)) as executor:
    #     futures = [executor.submit(get_eligible_fcl_freight_rate_free_day_data, free_day) for free_day in detention_and_demurrage_free_days]
    #     method_responses = {}
    #     for i in range(0,len(futures)):
    #         method_responses[detention_and_demurrage_free_days[i]['interaction']] = futures[i].result()
    #         # method_responses.update(result)


    query, total_count = apply_pagination(query, page, page_limit)

    final_data = get_final_data(query)

    response = add_pagination_data(
        response, page, total_count, page_limit, final_data, pagination_data_required
    )

    return response


