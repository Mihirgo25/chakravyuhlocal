from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedbacks
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from configs.air_freight_rate_constants import RATE_ENTITY_MAPPING,AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
from playhouse.shortcuts import model_to_dict
from libs.get_filters import get_filters
from typing import Optional
from libs.get_applicable_filters import get_applicable_filters
from database.rails_db import get_partner_user_experties, get_organization_service_experties
from datetime import datetime
import concurrent.futures, json
from peewee import fn, SQL,Window
from math import ceil
from micro_services.client import spot_search
from database.rails_db import get_organization
import pdb
from fastapi.encoders import jsonable_encoder
possible_direct_filters = ['feedback_type', 'performed_by_org_id', 'performed_by_id', 'closed_by_id', 'status']
possible_indirect_filters = ['relevant_supply_agent','origin_airport_id', 'destination_airport_id', 'validity_start_greater_than', 'validity_end_less_than', 'origin_trade_id', 'destination_trade_id', 'similar_id', 'origin_country_id', 'destination_country_id', 'service_provider_id', 'cogo_entity_id']


def list_air_freight_rate_feedbacks(filters = {},spot_search_details_required=False, page_limit =10, page=1, performed_by_id=None, is_stats_required=True, booking_details_required=False):
    query = AirFreightRateFeedbacks.select()

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, AirFreightRateFeedbacks)
        query = apply_indirect_filters(query, indirect_filters)

    stats = get_stats(filters, is_stats_required, performed_by_id) or {}
    pagination_data = get_pagination_data(query, page, page_limit)

    query = get_page(query, page, page_limit)
    data = get_data(query,spot_search_details_required,booking_details_required) 

    return {'list': jsonable_encoder(data) } | (pagination_data) | (stats)

def get_page(query, page, page_limit):
    query = query.order_by(AirFreightRateFeedbacks.created_at.desc(nulls='LAST')).paginate(page, page_limit)
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
    query = query.where((AirFreightRateFeedbacks.origin_airport_id << origin_airport_id) |
                    (AirFreightRateFeedbacks.origin_country_id << origin_airport_id) |
                    (AirFreightRateFeedbacks.origin_continent_id << origin_airport_id) |
                    (AirFreightRateFeedbacks.origin_trade_id << origin_airport_id))
    query = query.where((AirFreightRateFeedbacks.destination_airport_id << destination_airport_id) |
                    (AirFreightRateFeedbacks.destination_country_id << destination_airport_id) |
                    (AirFreightRateFeedbacks.destination_continent_id << destination_airport_id) |
                    (AirFreightRateFeedbacks.destination_trade_id << destination_airport_id))
    return query


def apply_cogo_entity_id_filter(query, filters):
    filter_entity_id = filters['cogo_entity_id']
    query = query.where((AirFreightRateFeedbacks.cogo_entity_id == filter_entity_id) | (AirFreightRateFeedbacks.cogo_entity_id.is_null(True)))
    return query

def apply_service_provider_id_filter(query, filters):
    query = query.where(AirFreightRateFeedbacks.service_provider_id == filters['service_provider_id'])
    return query

def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(AirFreightRateFeedbacks.created_at.cast('date') >= datetime.fromisoformat(filters['validity_start_greater_than']).date())

    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(AirFreightRateFeedbacks.created_at.cast('date') <= datetime.fromisoformat(filters['validity_end_less_than']).date())

    return query

def apply_origin_airport_id_filter(query, filters):
    query = query.where(AirFreightRateFeedbacks.origin_airport_id == filters['origin_airport_id'])
    return query

def apply_destination_airport_id_filter(query, filters):
    query = query.where(AirFreightRateFeedbacks.destination_airport_id == filters['destination_airport_id'])
    return query

def apply_origin_country_id_filter(query, filters):
    query = query.where(AirFreightRateFeedbacks.origin_country_id == filters['origin_country_id'])
    return query

def apply_destination_country_id_filter(query, filters):
    query = query.where(AirFreightRateFeedbacks.destination_country_id == filters['destination_country_id'])
    return query

def apply_airline_id_filter(query,filters):
    query = query.where(AirFreightRateFeedbacks.airline_id == filters['airline_id'])

def apply_similar_id_filter(query, filters):
    feedback_data = (AirFreightRateFeedbacks.select(AirFreightRateFeedbacks.origin_airport_id, AirFreightRateFeedbacks.destination_airport_id, AirFreightRateFeedbacks.operation_type , AirFreightRateFeedbacks.commodity).where(AirFreightRateFeedbacks.id == filters['similar_id'])).first()
    if feedback_data:
        query = query.where(AirFreightRateFeedbacks.id != filters.get('similar_id'))
        query = query.where(AirFreightRateFeedbacks.origin_airport_id == feedback_data.origin_airport_id, AirFreightRateFeedbacks.destination_airport_id == feedback_data.destination_airport_id, AirFreightRateFeedbacks.operation_type == feedback_data.operation_type, AirFreightRateFeedbacks.commodity == feedback_data.commodity)
    return query

def get_data(query, spot_search_details_required, booking_details_required):
    if not booking_details_required:
        query = query.select(
            AirFreightRateFeedbacks.id,
            AirFreightRateFeedbacks.cogo_entity_id,
            AirFreightRateFeedbacks.closed_by_id,
            AirFreightRateFeedbacks.closed_by,
            AirFreightRateFeedbacks.closing_remarks,
            AirFreightRateFeedbacks.created_at,
            AirFreightRateFeedbacks.air_freight_rate_id,
            AirFreightRateFeedbacks.feedback_type,
            AirFreightRateFeedbacks.feedbacks,
            AirFreightRateFeedbacks.performed_by_id,
            AirFreightRateFeedbacks.performed_by,
            AirFreightRateFeedbacks.performed_by_org_id,
            AirFreightRateFeedbacks.performed_by_org,
            AirFreightRateFeedbacks.performed_by_type,
            AirFreightRateFeedbacks.preferred_freight_rate,
            AirFreightRateFeedbacks.preferred_freight_rate_currency,
            AirFreightRateFeedbacks.preferred_airline_ids,
            AirFreightRateFeedbacks.preferred_airlines,
            AirFreightRateFeedbacks.remarks,
            AirFreightRateFeedbacks.serial_id,
            AirFreightRateFeedbacks.source,
            AirFreightRateFeedbacks.source_id,
            AirFreightRateFeedbacks.status,
            AirFreightRateFeedbacks.updated_at,
            AirFreightRateFeedbacks.validity_id,
            AirFreightRateFeedbacks.origin_airport_id,
            AirFreightRateFeedbacks.origin_continent_id,
            AirFreightRateFeedbacks.origin_trade_id,
            AirFreightRateFeedbacks.origin_country_id,
            AirFreightRateFeedbacks.destination_airport_id,
            AirFreightRateFeedbacks.destination_continent_id,
            AirFreightRateFeedbacks.destination_trade_id,
            AirFreightRateFeedbacks.destination_country_id,
            AirFreightRateFeedbacks.commodity,
            AirFreightRateFeedbacks.operation_type,
            AirFreightRateFeedbacks.service_provider_id,
            AirFreightRateFeedbacks.origin_airport,
            AirFreightRateFeedbacks.destination_airport,
            AirFreightRateFeedbacks.weight,
            AirFreightRateFeedbacks.volume,
            AirFreightRateFeedbacks.airline_id,
            AirFreightRateFeedbacks.reverted_rate_id
        )
    data = list(query.dicts())
    service_provider_ids = []
    air_freight_rate_ids = [row['air_freight_rate_id'] for row in data]
    air_freight_rates = list(AirFreightRate.select(AirFreightRate.id,AirFreightRate.validities).where(AirFreightRate.id.in_(air_freight_rate_ids)).dicts())
    air_freight_rate_mappings = {k['id']: k for k in air_freight_rates}
    for item in data:
        if 'booking_params' in item and 'rate_card' in item['booking_params'] and item['booking_params']['rate_card'] and 'service_rates' in item['booking_params']['rate_card'] and item['booking_params']['rate_card']['service_rates']:
            service_rates = item['booking_params']['rate_card']['service_rates'] or {}
            rates = service_rates.values()
            for rate in rates:
                if 'service_provider_id' in rate:
                    service_provider_ids.append(rate['service_provider_id'])
    service_providers = []
    service_providers_hash = {}
    if len(service_provider_ids):
        service_providers = get_organization(service_provider_ids)
        for sp in service_providers:
            service_providers_hash[sp['id']] = sp
    spot_search_hash = {}
    new_data = []
    if spot_search_details_required:
        spot_search_ids = list(set([str(row['source_id']) for row in data]))
        spot_search_data = spot_search.list_spot_searches({'filters':{'id': spot_search_ids}})['list']
        for search in spot_search_data:
            spot_search_hash[search['id']] = {'id':search.get('id'), 'importer_exporter_id':search.get('importer_exporter_id'), 'importer_exporter':search.get('importer_exporter'), 'service_details':search.get('service_details')}

    for object in data:
        reverted_rate = None
        if object['reverted_rate_id']:
            reverted_rate = air_freight_rate_mappings[object['reverted_rate_id']]
        if 'booking_params' in object:
            if object['booking_params'].get('rate_card', {}).get('service_rates', {}):
                for key, value in object['booking_params']['rate_card']['service_rates'].items():
                    service_provider = value.get('service_provider_id', None)
                    if service_provider:
                        value['service_provider'] = service_providers_hash.get(service_provider)
        if spot_search_details_required:
            object['spot_search'] = spot_search_hash.get(str(object['source_id']), {})
        add_reverted_data(object,reverted_rate)
        new_data.append(object)
    return new_data


def get_chargeable_weight(weight: Optional[float], volume: Optional[float]) -> Optional[float]:
    if not weight or not volume:
        return None

    volumetric_weight = volume * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
    chargeable_weight = max(volumetric_weight, weight)

    return round(chargeable_weight, 2)

def add_reverted_data(object, reverted_rate):
    object["reverted_rate_data"] = {}
    if reverted_rate:
        object["reverted_rate_data"]["commodity"] = reverted_rate.get("commodity")
        object["reverted_rate_data"]["commodity_type"] = reverted_rate.get("commodity_type")
        object["reverted_rate_data"]["commodity_sub_type"] = reverted_rate.get("commodity_sub_type")
        object["reverted_rate_data"]["operation_type"] = reverted_rate.get("operation_type")
        object["reverted_rate_data"]["stacking_type"] = reverted_rate.get("stacking_type")
        object["reverted_rate_data"]["shipment_type"] = reverted_rate.get("shipment_type")
        object["reverted_rate_data"]["price_type"] = reverted_rate.get("price_type", None)
        reverted_validity_data = next((t for t in reverted_rate.get("validities", []) if t.get("id") == object.get("reverted_validity_id")), {})
        object["reverted_rate_data"]["min_price"] = reverted_validity_data.get("min_price", None)
        object["reverted_rate_data"]["weight_slabs"] = reverted_validity_data.get("weight_slabs", [])
        chargeable_weight = get_chargeable_weight(object.get("weight"), object.get("volume"))
        for weight_slab in reverted_validity_data.get("weight_slabs", []):
            if weight_slab.get("lower_limit") >= chargeable_weight and weight_slab.get("upper_limit") <= chargeable_weight:
                object["price"] = weight_slab.get("tarrif_price", None)
                break
        object["reverted_rate_data"]["currency"] = reverted_validity_data.get("currency", None)

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

    query = AirFreightRateFeedbacks.select()

    if filters:
        if 'status' in filters:
            del filters['status']
        if 'closed_by_id' in filters:
            del filters['closed_by_id']

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, AirFreightRateFeedbacks)
        query = apply_indirect_filters(query, indirect_filters)

    query = (
        query
        .select(
            fn.count(AirFreightRateFeedbacks.id).over().alias('get_total'),
          fn.count(AirFreightRateFeedbacks.id).filter(AirFreightRateFeedbacks.status == 'active').over().alias('get_status_count_active'),
        fn.count(AirFreightRateFeedbacks.id).filter(AirFreightRateFeedbacks.status == 'inactive').over().alias('get_status_count_inactive'),
        fn.count(AirFreightRateFeedbacks.id).filter((AirFreightRateFeedbacks.status=='inactive') & (AirFreightRateFeedbacks.closed_by_id==performed_by_id)).over().alias('get_total_closed_by_user'),
        fn.count(AirFreightRateFeedbacks.id).filter((AirFreightRateFeedbacks.status=='active')  & (AirFreightRateFeedbacks.performed_by_id==performed_by_id)).over().alias('get_total_opened_by_user'),

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


