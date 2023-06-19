from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from libs.get_filters import get_filters
from libs.get_applicable_filters import get_applicable_filters
from libs.json_encoder import json_encoder
import json
from datetime import datetime
from math import ceil
from micro_services.client import common

possible_direct_filters = ['feedback_type', 'status', 'origin_port_id', 'destination_port_id', 'commodity', 'container_size', 'container_type', 'source']
possible_indirect_filters = ['created_at_greater_than', 'created_at_less_than']

def list_fcl_freight_rate_deviations(filters = {}, page_limit=10, page=1):
    query = FclFreightRateFeedback.select(
        FclFreightRateFeedback.id,
        FclFreightRateFeedback.booking_params,
        FclFreightRateFeedback.closed_by,
        FclFreightRateFeedback.created_at,
        FclFreightRateFeedback.performed_by,
        FclFreightRateFeedback.preferred_freight_rate,
        FclFreightRateFeedback.preferred_freight_rate_currency,
        FclFreightRateFeedback.source,
        FclFreightRateFeedback.commodity,
        FclFreightRateFeedback.container_size,
        FclFreightRateFeedback.container_type,
        FclFreightRateFeedback.origin_port,
        FclFreightRateFeedback.destination_port,
        FclFreightRateFeedback.reverted_validities
    ).where(
        FclFreightRateFeedback.feedback_type == 'disliked',
        FclFreightRateFeedback.reverted_validities.is_null(False) | FclFreightRateFeedback.preferred_freight_rate.is_null(False))

    if filters:
        if type(filters) != dict:
            filters = json.loads(filters)

        direct_filters, indirect_filters = get_applicable_filters(filters, possible_direct_filters, possible_indirect_filters)

        query = get_filters(direct_filters, query, FclFreightRateFeedback)
        query = apply_indirect_filters(query, indirect_filters)

    pagination_data = get_pagination_data(query, page, page_limit)
    query = query.paginate(page,page_limit)

    data = get_data(query)

    return { 'list': json_encoder(data) } | (pagination_data)

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_created_at_greater_than_filter(query, filters):
    query = query.where(FclFreightRateFeedback.created_at.cast('date') >= datetime.fromisoformat(filters['created_at_greater_than']).date())
    return query

def apply_created_at_less_than_filter(query, filters):
    query = query.where(FclFreightRateFeedback.created_at.cast('date') <= datetime.fromisoformat(filters['created_at_less_than']).date())
    return query

def get_data(query):
    data = list(query.dicts())

    for object in data:
        if 'booking_params' in object and 'rate_card' in object['booking_params'] and object['booking_params']['rate_card']:
            for line_item in object['booking_params']['rate_card'].get('line_items'):
                if line_item['code'] == 'BAS':
                    object['old_price'] = line_item['price']
                    object['old_price_currency'] = line_item['currency']
                    break
        if object.get('reverted_validities') and len(object['reverted_validities']) > 0:
            for feedback_line_item in object['reverted_validities'][0]['line_items']:
                if feedback_line_item['code'] == "BAS":
                    object['new_price'] = feedback_line_item['price']
                    object['new_price_currency'] = feedback_line_item['currency']
                    break
        if object.get('old_price') and object.get('new_price'):
            if object['old_price_currency'] != object['new_price_currency']:
                object['new_price'] = common.get_money_exchange_for_fcl({"price":object['new_price'], "from_currency":object['new_price_currency'], "to_currency":object['old_price_currency']})['price']
            object['deviation'] = (object['new_price'] - object['old_price'])/object['new_price'] * 100
    return data

def get_pagination_data(query, page, page_limit):
    total_count = query.count()
    
    pagination_data = {
        'page': page,
        'total': ceil(total_count/page_limit),
        'total_count': total_count,
        'page_limit': page_limit
        }
    
    return pagination_data
