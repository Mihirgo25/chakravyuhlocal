from services.air_freight_rate.models.air_freight_rate_local_feedback import AirFreightRateLocalFeedback
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from database.rails_db import get_partner_user_experties
from datetime import datetime
import json
from peewee import fn
from math import ceil
from micro_services.client import spot_search
from libs.json_encoder import json_encoder
from services.air_freight_rate.constants.air_freight_rate_constants import IMPORTER_EXPORTER_ID_FOR_FREIGHT_FORCE, IMPORTER_EXPORTER_ID_FOR_ENTERPRISE_SALES

possible_direct_filters = ['id', 'feedback_type', 'performed_by_org_id', 'performed_by_id', 'closed_by_id', 'status','trade_type','airport_id', 'trade_id', 'country_id', 'service_provider_id', 'cogo_entity_id','airline_id', 'serial_id', 'spot_search_serial_id']
possible_indirect_filters = ['relevant_supply_agent', 'validity_start_greater_than', 'validity_end_less_than', 'similar_id', 'freight_force_importer_exporter', 'except_freight_force_importer_exporter', 'q']

def list_air_freight_rate_local_feedbacks(filters = {}, spot_search_details_required=False, page_limit =10, page=1, performed_by_id=None, is_stats_required=True):
    query = AirFreightRateLocalFeedback.select()
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, AirFreightRateLocalFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    stats = get_stats(filters, is_stats_required, performed_by_id) or {}
    pagination_data = get_pagination_data(query, page, page_limit)

    query = get_page(query, page, page_limit)
    data = get_data(query,spot_search_details_required)

    return {'list': json_encoder(data) } | (pagination_data) | (stats)

def get_page(query, page, page_limit):
    query = query.order_by(AirFreightRateLocalFeedback.created_at.desc(nulls='LAST')).paginate(page, page_limit)
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('air_freight_local', filters['relevant_supply_agent'])
    airport_id = [t['location_id'] for t in expertises]
    query = query.where((AirFreightRateLocalFeedback.airport_id << airport_id) |
                    (AirFreightRateLocalFeedback.country_id << airport_id) |
                    (AirFreightRateLocalFeedback.continent_id << airport_id) |
                    (AirFreightRateLocalFeedback.trade_id << airport_id))
    return query

def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(AirFreightRateLocalFeedback.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than']).date())
    return query

def apply_q_filter(query, filters):
    q = str(filters.get('q', ''))
    query = query.where(AirFreightRateLocalFeedback.serial_id.cast("text") ** (q + "%"))
    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(AirFreightRateLocalFeedback.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than']).date())
    return query

def apply_freight_force_importer_exporter_filter(query, filters):
    return query.where(AirFreightRateLocalFeedback.performed_by_org_id in IMPORTER_EXPORTER_ID_FOR_FREIGHT_FORCE)

def apply_except_freight_force_importer_exporter_filter(query, filters):
    return query.where(AirFreightRateLocalFeedback.performed_by_org_id not in IMPORTER_EXPORTER_ID_FOR_FREIGHT_FORCE)

def apply_similar_id_filter(query, filters):
    local_feedback_data = (AirFreightRateLocalFeedback.select(AirFreightRateLocalFeedback.airport_id, AirFreightRateLocalFeedback.commodity).where(AirFreightRateLocalFeedback.id == filters['similar_id'])).first()
    if local_feedback_data:
        query = query.where(AirFreightRateLocalFeedback.id != filters.get('similar_id'))
        query = query.where(AirFreightRateLocalFeedback.airport_id == local_feedback_data.airport_id, AirFreightRateLocalFeedback.commodity == local_feedback_data.commodity)
    return query

def get_data(query, spot_search_details_required):
    data = json_encoder(list(query.dicts()))
    air_freight_rate_local_ids = []
    for rate in data:
        if rate['air_freight_rate_local_id']:
            air_freight_rate_local_ids.append((rate['air_freight_rate_local_id']))
        if rate.get('reverted_rate'):
            air_freight_rate_local_ids.append((rate['reverted_rate'].get('id')))
    air_freight_rate_locals = AirFreightRateLocal.select(AirFreightRateLocal.id,
                                            AirFreightRateLocal.airport,
                                            AirFreightRateLocal.commodity,
                                            AirFreightRateLocal.commodity_type,
                                            AirFreightRateLocal.airline,
                                            AirFreightRateLocal.service_provider
                                        ).where(AirFreightRateLocal.id.in_(air_freight_rate_local_ids))

    air_freight_local_rates = json_encoder(list(air_freight_rate_locals.dicts()))
    air_freight_rate_local_mappings = {k['id']: k for k in air_freight_local_rates}
    spot_search_hash = {}
    new_data = []
    if spot_search_details_required:
        spot_search_ids = list(set([str(row['source_id']) for row in data]))
        spot_search_data = spot_search.list_spot_searches({'filters':{'id': spot_search_ids}})['list']
        for search in spot_search_data:
            spot_search_hash[search['id']] = {'id':search.get('id'), 'importer_exporter_id':search.get('importer_exporter_id'), 'importer_exporter':search.get('importer_exporter'), 'service_details':search.get('service_details')}

    for object in data:
        rate = air_freight_rate_local_mappings[(object['air_freight_rate_local_id'])]
        object['airport'] = rate['airport']
        object['commodity'] = rate['commodity']
        object['commodity_type'] = rate['commodity_type']
        object['airline'] = rate['airline']
        object['price'] = None
        object['currency'] = None
        object['volume'] = object['booking_params'].get('volume')
        object['weight'] = object['booking_params'].get('weight')

        if spot_search_details_required:
            object['spot_search'] = spot_search_hash.get((object['source_id']), {})

        if object.get('reverted_rate'):
            reverted_rate = air_freight_rate_local_mappings[(object['reverted_rate'].get('id'))]
            object['reverted_rate_data']={}
            object['reverted_rate_data']['commodity'] = reverted_rate['commodity']
            object['reverted_rate_data']['commodity_type'] = reverted_rate['commodity_type']

            object['chargeable_weight'] = get_chargeable_weight(object['weight'], object['volume'])
        if str(object['performed_by_org_id']) in IMPORTER_EXPORTER_ID_FOR_FREIGHT_FORCE:
            object['service_provider'] = 'FREIGHT_FORCE'
        elif str(object['performed_by_org_id']) in IMPORTER_EXPORTER_ID_FOR_ENTERPRISE_SALES:
            object['service_provider'] = 'ENTERPRISE_SALES'

        new_data.append(object)
    return new_data

def get_chargeable_weight(weight, volume):
    if not weight or not volume:
        return None

    volumetric_weight = volume * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
    chargeable_weight = max(volumetric_weight, weight)

    return round(chargeable_weight, 2)

def get_pagination_data(query, page, page_limit):
    total_count = query.count()
    params = {
      'page': page,
      'total': ceil(total_count/page_limit),
      'total_count': total_count,
      'page_limit': page_limit
    }
    return params

def get_stats(filters, is_stats_required, performed_by_id):
    if not is_stats_required:
        return {}

    query = AirFreightRateLocalFeedback.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        if 'closed_by_id' in filters:
            del filters['closed_by_id']

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, AirFreightRateLocalFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    query = (
        query
        .select(
            fn.count(AirFreightRateLocalFeedback.id).over().alias('get_total'),
            fn.count(AirFreightRateLocalFeedback.id).filter(AirFreightRateLocalFeedback.status == 'active').over().alias('get_status_count_active'),
            fn.count(AirFreightRateLocalFeedback.id).filter(AirFreightRateLocalFeedback.status == 'inactive').over().alias('get_status_count_inactive'),
            fn.count(AirFreightRateLocalFeedback.id).filter((AirFreightRateLocalFeedback.status=='inactive') & (AirFreightRateLocalFeedback.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
            fn.count(AirFreightRateLocalFeedback.id).filter((AirFreightRateLocalFeedback.status=='active')  & (AirFreightRateLocalFeedback.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),
        )
    ).limit(1)

    result = query.execute()
    if len(result) > 0:
        result = result[0]
        stats = {
            'total': result.get_total,
            'total_closed_by_user': result.get_total_closed_by_user,
            'total_opened_by_user': result.get_total_opened_by_user,
            'total_open': result.get_status_count_active,
            'total_closed': result.get_status_count_inactive
        }
    else:
        stats = {}
    return {'stats': stats}