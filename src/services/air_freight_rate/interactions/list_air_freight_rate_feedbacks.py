from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
from playhouse.shortcuts import model_to_dict
from libs.get_filters import get_filters
from typing import Optional
from libs.get_applicable_filters import get_applicable_filters
from database.rails_db import get_partner_user_experties, get_organization_service_experties
from datetime import datetime
import concurrent.futures, json
from peewee import fn, SQL,Window
from math import ceil
from configs.global_constants import RATE_ENTITY_MAPPING
from micro_services.client import spot_search
from database.rails_db import get_organization
from libs.json_encoder import json_encoder
from services.air_freight_rate.constants.air_freight_rate_constants import IMPORTER_EXPORTER_ID_FOR_FREIGHT_FORCE

possible_direct_filters = ['feedback_type', 'performed_by_org_id', 'performed_by_id', 'closed_by_id', 'status','trade_type','origin_airport_id', 'destination_airport_id','origin_trade_id', 'destination_trade_id', 'origin_country_id', 'destination_country_id', 'service_provider_id', 'cogo_entity_id','airline_id']
possible_indirect_filters = ['relevant_supply_agent', 'validity_start_greater_than', 'validity_end_less_than', 'similar_id', 'freight_force_importer_exporter', 'except_freight_force_importer_exporter']

def list_air_freight_rate_feedbacks(filters = {},spot_search_details_required=False, page_limit =10, page=1, performed_by_id=None, is_stats_required=True, booking_details_required=False):
    query = AirFreightRateFeedback.select()
    
    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, AirFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    stats = get_stats(filters, is_stats_required, performed_by_id) or {}
    pagination_data = get_pagination_data(query, page, page_limit)

    query = get_page(query, page, page_limit)
    data = get_data(query,spot_search_details_required,booking_details_required) 

    return {'list': json_encoder(data) } | (pagination_data) | (stats)

def get_page(query, page, page_limit):
    query = query.order_by(AirFreightRateFeedback.created_at.desc(nulls='LAST')).paginate(page, page_limit)
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_relevant_supply_agent_filter(query, filters):
    expertises = get_partner_user_experties('air_freight', filters['relevant_supply_agent'])
    origin_airport_id = [t['origin_location_id'] for t in expertises]
    destination_airport_id = [t['destination_location_id'] for t in expertises]
    query = query.where((AirFreightRateFeedback.origin_airport_id << origin_airport_id) |
                    (AirFreightRateFeedback.origin_country_id << origin_airport_id) |
                    (AirFreightRateFeedback.origin_continent_id << origin_airport_id) |
                    (AirFreightRateFeedback.origin_trade_id << origin_airport_id))
    query = query.where((AirFreightRateFeedback.destination_airport_id << destination_airport_id) |
                    (AirFreightRateFeedback.destination_country_id << destination_airport_id) |
                    (AirFreightRateFeedback.destination_continent_id << destination_airport_id) |
                    (AirFreightRateFeedback.destination_trade_id << destination_airport_id))
    return query


def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(AirFreightRateFeedback.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than']).date())

    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(AirFreightRateFeedback.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than']).date())

    return query

def apply_freight_force_importer_exporter_filter(query, filters):
    return query.where(AirFreightRateFeedback.performed_by_org_id in IMPORTER_EXPORTER_ID_FOR_FREIGHT_FORCE)

def apply_except_freight_force_importer_exporter_filter(query, filters):
    return query.where(AirFreightRateFeedback.performed_by_org_id not in IMPORTER_EXPORTER_ID_FOR_FREIGHT_FORCE)


def apply_similar_id_filter(query, filters):
    feedback_data = (AirFreightRateFeedback.select(AirFreightRateFeedback.origin_airport_id, AirFreightRateFeedback.destination_airport_id, AirFreightRateFeedback.operation_type , AirFreightRateFeedback.commodity).where(AirFreightRateFeedback.id == filters['similar_id'])).first()
    if feedback_data:
        query = query.where(AirFreightRateFeedback.id != filters.get('similar_id'))
        query = query.where(AirFreightRateFeedback.origin_airport_id == feedback_data.origin_airport_id, AirFreightRateFeedback.destination_airport_id == feedback_data.destination_airport_id, AirFreightRateFeedback.operation_type == feedback_data.operation_type, AirFreightRateFeedback.commodity == feedback_data.commodity)
    return query

def get_data(query, spot_search_details_required, booking_details_required):
    data =json_encoder(list(query.dicts()))
    air_freight_rate_ids = []
    for rate in data:
        if rate['air_freight_rate_id']:
            air_freight_rate_ids.append((rate['air_freight_rate_id']))
        if rate.get('reverted_rate_id'):
            air_freight_rate_ids.append((rate['reverted_rate_id']))
    air_freight_rates = AirFreightRate.select(AirFreightRate.id,
                                            AirFreightRate.validities,
                                            AirFreightRate.origin_airport,
                                            AirFreightRate.destination_airport,
                                            AirFreightRate.commodity,
                                            AirFreightRate.commodity_type,
                                            AirFreightRate.commodity_sub_type,
                                            AirFreightRate.stacking_type,
                                            AirFreightRate.shipment_type,
                                            AirFreightRate.price_type,
                                            AirFreightRate.airline,
                                            AirFreightRate.operation_type,
                                            AirFreightRate.service_provider
            ).where(AirFreightRate.id.in_(air_freight_rate_ids))
    
    air_freight_rates = json_encoder(list(air_freight_rates.dicts()))
    air_freight_rate_mappings = {k['id']: k for k in air_freight_rates}
    spot_search_hash = {}
    new_data = []
    if spot_search_details_required:
        spot_search_ids = list(set([str(row['source_id']) for row in data]))
        spot_search_data = spot_search.list_spot_searches({'filters':{'id': spot_search_ids}})['list']
        for search in spot_search_data:
            spot_search_hash[search['id']] = {'id':search.get('id'), 'importer_exporter_id':search.get('importer_exporter_id'), 'importer_exporter':search.get('importer_exporter'), 'service_details':search.get('service_details')}

    for object in data:
        rate = air_freight_rate_mappings[(object['air_freight_rate_id'])]
        object['origin_airport'] = rate['origin_airport']
        object['destination_airport'] =rate['destination_airport']
        object['commodity'] = rate['commodity']
        object['commodity_type'] = rate['commodity_type']
        object['commodity_sub_type'] = rate['commodity_sub_type']
        object['operation_type'] = rate['operation_type']
        object['stacking_type'] = rate['stacking_type']
        object['shipment_type'] = rate['shipment_type']
        object['price_type'] = rate['price_type']
        object['airline'] = rate['airline']
        object['price'] = None
        object['currency'] = None
        object['volume'] = object['booking_params'].get('volume')
        object['weight'] = object['booking_params'].get('weight')
        for validity in rate['validities']:
            if validity['id'] == object['validity_id']:
                object['price'] = validity['min_price']
                object['currency'] = validity['currency']
                break
        if spot_search_details_required:
            object['spot_search'] = spot_search_hash.get((object['source_id']), {})
        
        if object.get('reverted_rate_id'):
            reverted_rate = air_freight_rate_mappings[(object['reverted_rate_id'])]
            object['reverted_rate_data']={}
            object['reverted_rate_data']['commodity'] = reverted_rate['commodity']
            object['reverted_rate_data']['commodity_type'] = reverted_rate['commodity_type']
            object['reverted_rate_data']['commodity_sub_type'] = reverted_rate['commodity_sub_type']
            object['reverted_rate_data']['operation_type'] = reverted_rate['operation_type']
            object['reverted_rate_data']['stacking_type'] = reverted_rate['stacking_type']
            object['reverted_rate_data']['shipment_type'] = reverted_rate['shipment_type']
            object['reverted_rate_data']['price_type'] = reverted_rate.get('price_type')
            reverted_validity_data= {
                'weight_slabs': []
            }
            for validity_data in reverted_rate['validities']:
                if validity_data['id']== (object.get('reverted_rate') or {}).get('validity_id'):
                    reverted_validity_data=validity_data
                    break
            object['reverted_rate_data']['min_price'] = reverted_validity_data.get('min_price') 
            object['reverted_rate_data']['weight_slabs'] = reverted_validity_data.get('weight_slabs')
            object['chargeable_weight'] = get_chargeable_weight(object['weight'], object['volume'])
            for  weight_slab in reverted_validity_data['weight_slabs']:
                if weight_slab['lower_limit']<=object['chargeable_weight'] and weight_slab['upper_limit']<=object['chargeable_weight']:
                    object['price']=weight_slab['tariff_price']
                    break
            object['reverted_rate_data']['currency'] = reverted_validity_data.get('currency')
        if str(object['performed_by_org_id']) in IMPORTER_EXPORTER_ID_FOR_FREIGHT_FORCE:
            object['service_provider'] = 'FREIGHT_FORCE'

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

    query = AirFreightRateFeedback.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        if 'closed_by_id' in filters:
            del filters['closed_by_id']

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, AirFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    query = (
        query
        .select(
            fn.count(AirFreightRateFeedback.id).over().alias('get_total'),
          fn.count(AirFreightRateFeedback.id).filter(AirFreightRateFeedback.status == 'active').over().alias('get_status_count_active'),
        fn.count(AirFreightRateFeedback.id).filter(AirFreightRateFeedback.status == 'inactive').over().alias('get_status_count_inactive'),
        fn.count(AirFreightRateFeedback.id).filter((AirFreightRateFeedback.status=='inactive') & (AirFreightRateFeedback.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
        fn.count(AirFreightRateFeedback.id).filter((AirFreightRateFeedback.status=='active')  & (AirFreightRateFeedback.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),

         )
    ).limit(1)


    result = query.execute()
    if len(result)>0:
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
    return { 'stats': stats }