from services.rate_sheet.models.rate_sheet import RateSheet
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from libs.get_filters import get_filters
from fastapi.encoders import jsonable_encoder
import services.rate_sheet.interactions.list_rate_sheets as list_rate_sheet
import json, uuid, math
import concurrent.futures
from micro_services.client import *
from database.rails_db import get_organization ,get_user
from datetime import datetime, timedelta
from peewee import *
from database.db_session import rd
from services.rate_sheet.interactions.fcl_rate_sheet_converted_file import get_total_line, get_current_processing_line
from services.rate_sheet.interactions.fcl_rate_sheet_converted_file import get_processed_percent

POSSIBLE_DIRECT_FILTERS = ['id', 'agent_id', 'service_provider_id', 'status', 'service_name', 'serial_id', 'cogo_entity_id']
POSSIBLE_INDIRECT_FILTERS = ['performed_by_id', 'partner_id']




def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def apply_direct_filters(query, filters):
    query = get_filters(filters, query, RateSheet)
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
            if key == "serial_id":
                try:
                    val = int(val)
                    direct_filters[key] = val
                except:
                    direct_filters[key] = 0
            else:
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
    query =query.order_by(SQL("updated_at desc"))
    query = query.offset(offset).limit(page_limit)
    return query, total_count



def detail(data):
    for d in data:

        total_percentage = 0
        if d['converted_files']:
            for converted_file in d['converted_files']:
                try:
                    total_percentage += converted_file.get('valid_rates_count')/converted_file.get('rates_count')*100
                except:
                    total_percentage += 0
                converted_file['total_lines'] = get_total_line(converted_file)
                converted_file['last_line'] = get_current_processing_line(converted_file)
            d['completed_percent'] = total_percentage/len(d['converted_files'])
            if d['status'] == 'processing':
                d['processed_percent'] = get_processed_percent(d)
            else:
                d['processed_percent'] = d['completed_percent']
    return data


def add_service_objects(data):
    if len(data) == 0:
        return data
    objects_organizations_hash = {}
    objects_user_hash = {}
    org_ids = []
    user_ids = []
    for cluster in data:
        try:
            org_id = cluster.get('service_provider_id')
            if org_id:
                org_ids.append(org_id)
            user_id = [str(cluster.get('procured_by_id')), str(cluster.get('sourced_by_id')), str(cluster.get('performed_by_id'))]
            if user_id:
                user_ids+=user_id
        except:
            continue

    if len(org_ids):
        list_organizations = get_organization(id=org_ids)
        for org in list_organizations:
            objects_organizations_hash[org['id']] =org

    if len(user_ids):
        objects_user = []
        for id in user_ids:
            if is_valid_uuid(id):
                objects_user.append(id)
        list_user = get_user(objects_user)
        for user_obj in list_user:
            objects_user_hash[user_obj['id']] =user_obj
    for object in data:
        service_provider = {}
        if objects_organizations_hash.get(object.get('service_provider_id')):
            for key, val in objects_organizations_hash.get(object.get('service_provider_id')).items():
                if key in ['id', 'business_name', 'short_name', 'logo_url']:
                    service_provider[key] = val
        object['service_provider'] = service_provider
        object['procured_by'] = objects_user_hash.get(str(object.get('procured_by_id')))
        object['sourced_by'] = objects_user_hash.get(str(object.get('sourced_by_id')))
        object['performed_by'] = objects_user_hash.get(str(object.get('performed_by_id')))
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
        object['updated_at'] = datetime.fromisoformat(object['updated_at']) +timedelta(hours=5, minutes=30)

        if 'converted_files' in object:
            if object.get('converted_files'):
                for obj in object.get('converted_files'):
                    rates_count_sum+=obj.get('rates_count')
            object['rates_count'] = rates_count_sum
        rate_sheet_audit = rate_sheet_audits.where(RateSheetAudit.object_id == object['id']).order_by(RateSheetAudit.created_at.desc()).limit(1).dicts().get()
        object['sourced_by_id'] = rate_sheet_audit.get('sourced_by_id')
        object['procured_by_id'] = rate_sheet_audit.get('procured_by_id')
        object['performed_by_id'] = rate_sheet_audit.get('performed_by_id')
    final_data = add_service_objects(final_data)
    final_data = jsonable_encoder(final_data)
    return final_data

def add_pagination_data(
    response, page, total_count, page_limit
):
    response["page"] = page
    response["total"] = math.ceil(total_count / page_limit)
    response["total_count"] = total_count
    response["page_limit"] = page_limit
    


def list_rate_sheets(filters, stats_required= None, page=1, page_limit=10, sort_by=None, sort_type=None, pagination_data_required=True):
    response = {"success": False, "status_code": 200}
    if filters is None:
        filters = {}
    if isinstance(filters, str):
        filters = json.loads(filters)

    query = RateSheet.select()
    if len(filters) != 0:
        direct_filters, indirect_filters = get_direct_indirect_filters(filters)
        query = apply_direct_filters(query, direct_filters)
        query = apply_indirect_filters(
            query, indirect_filters
        )

    if page_limit:
        query, total_count = apply_pagination(query, page, page_limit)
    with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
        futures = executor.submit(get_final_data, query)
        final_data = futures.result()
        
    response["success"] = True
    response["list"] = final_data
    
    if pagination_data_required:
        response = add_pagination_data(
            response, page, total_count, page_limit, final_data, pagination_data_required
        )

    return response


