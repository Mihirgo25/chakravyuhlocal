from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from configs.fcl_freight_rate_constants import RATE_CONSTANT_MAPPING
from playhouse.shortcuts import model_to_dict
from rails_client import client
from datetime import datetime
import json
from operator import attrgetter
import concurrent.futures
from peewee import fn
from math import ceil


possible_direct_filters = ['feedback_type', 'performed_by_org_id', 'performed_by_id', 'closed_by_id', 'status']
possible_indirect_filters = ['relevant_supply_agent', 'origin_port_id', 'destination_port_id', 'validity_start_greater_than', 'validity_end_less_than', 'origin_trade_id', 'destination_trade_id', 'shipping_line_id', 'similar_id', 'origin_country_id', 'destination_country_id', 'service_provider_id', 'cogo_entity_id']

def remove_unexpected_filters(filters):
    filters = json.loads(filters)
    expected_filters = set(possible_direct_filters + possible_indirect_filters).intersection(set(filters.keys()))
    expected_filters = {key:filters[key] for key in list(expected_filters) if key in expected_filters}

    return expected_filters

def list_fcl_freight_rate_feedbacks(filters, page_limit, page, is_stats_required, performed_by_id, spot_search_details_required):
    filters = remove_unexpected_filters(filters)

    query = FclFreightRateFeedback.select()
    query = apply_direct_filters(query, filters)
    query = apply_indirect_filters(query, filters)
    query = get_join_query(query)
    stats = get_stats(query) or {}
    query = get_page(query)
    data = get_data(query)

def get_page(query, page, page_limit):
    query = query.order_by(FclFreightRateFeedback.created_at.desc()).paginate(page, page_limit)
    return query

def get_join_query(query):
    query = query.join(FclFreightRate, on=(FclFreightRateFeedback.fcl_freight_rate_id == FclFreightRate.id))
    return query

def apply_direct_filters(query,filters):
    for key in filters:
        if key in possible_direct_filters:
            query = query.select().where(attrgetter(key)(FclFreightRateFeedback) == filters[key])
    return query

def apply_indirect_filters(query, filters):
    for key in filters:
        if key in possible_indirect_filters:
            apply_filter_function = f'apply_{key}_filter'
            query = eval(f'{apply_filter_function}(query, filters)')
    return query

def apply_relevant_supply_agent_filter(query, filters):
    page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
    expertises = client.ruby.list_partner_user_expertises({ 'filters': { 'service_type': 'fcl_freight', 'partner_user_id': filters['relevant_supply_agent'] }, page_limit: page_limit })['list']
    origin_port_id = [t['origin_location_id'] for t in expertises]
    destination_port_id = [t['destination_location_id'] for t in expertises]
    query = query.where((FclFreightRate.origin_port_id == origin_port_id) |
                    (FclFreightRate.origin_country_id == origin_port_id) |
                    (FclFreightRate.origin_continent_id == origin_port_id) |
                    (FclFreightRate.origin_trade_id == origin_port_id))
    query = query.where((FclFreightRate.destination_port_id == destination_port_id) |
                    (FclFreightRate.destination_country_id == destination_port_id) |
                    (FclFreightRate.destination_continent_id == destination_port_id) |
                    (FclFreightRate.destination_trade_id == destination_port_id))
    return query

def apply_cogo_entity_id_filter(query, filters):
    filter_entity_id = filters['cogo_entity_id']

    cogo_entity_ids = [t["cogo_entity_id"] for t in RATE_CONSTANT_MAPPING if filter_entity_id in t["allowed_entity_ids"] if t["cogo_entity_id"]]
    query = query.where(FclFreightRate.cogo_entity_id == cogo_entity_ids)

    return query

def apply_service_provider_id_filter(query, filters):
    query = query.where(FclFreightRate.service_provider_id == filters['service_provider_id'])
    return query

def apply_validity_start_greater_than_filter(query, filters):
    query = query.where(FclFreightRateFeedback.created_at >= datetime.strptime(filters['validity_start_greater_than'],'%Y-%m-%d'))
    return query

def apply_validity_end_less_than_filter(query, filters):
    query = query.where(FclFreightRate.created_at <= datetime.strptime(filters['validity_end_less_than'],'%Y-%m-%d'))
    return query

def apply_origin_port_id_filter(query, filters):
    query = query.where(FclFreightRate.origin_port_id == filters['origin_port_id'])
    return query

def apply_destination_port_id_filter(query, filters):
    query = query.where(FclFreightRate.destination_port_id == filters['destination_port_id'])
    return query

def apply_origin_country_id_filter(query, filters):
    query = query.where(FclFreightRate.origin_country_id == filters['origin_country_id'])
    return query

def apply_destination_country_id_filter(query, filters):
    query = query.where(FclFreightRate.destination_country_id == filters['destination_country_id'])
    return query

def apply_origin_trade_id_filter(query, filters):
    query = query.where(FclFreightRate.origin_trade_id == filters['origin_trade_id'])
    return query

def apply_destination_trade_id_filter(query, filters):
    query = query.where(FclFreightRate.destination_trade_id == filters['destination_trade_id'])
    return query

def apply_shipping_line_id_filter(query, filters):
    query = query.where(FclFreightRate.shipping_line_id == filters['shipping_line_id'])
    return query

def apply_similar_id_filter(query, filters):
    feedback_data = (FclFreightRateFeedback
         .select(FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity)
         .join(FclFreightRate, on=(FclFreightRateFeedback.fcl_freight_rate_id == FclFreightRate.id))
         .where(FclFreightRateFeedback.id == filters['similar_id'])
         .first())

    query = query.where(~(FclFreightRateFeedback.id == filters.get('similar_id')))
    query = query.where(FclFreightRate.origin_port_id == feedback_data.origin_port_id, FclFreightRate.destination_port_id == feedback_data.destination_port_id, FclFreightRate.container_size == feedback_data.container_size, FclFreightRate.container_type == feedback_data.container_type, FclFreightRate.commodity == feedback_data.commodity)

    return query


def get_data(query):
    data = [model_to_dict(row, recurse=False) for row in query]
    add_service_objects(data)

# def add_service_objects(data)
#     fcl_freight_rates = FclFreightRate.where(id: data.pluck(:fcl_freight_rate_id)).as_json.map(&:deep_symbolize_keys)
#     fcl_freight_rate_mappings = fcl_freight_rates.each_with_object({}) { |k, h| h[k[:id]] = k }
#     shipping_line_ids = data.pluck(:preferred_shipping_line_ids).flatten + fcl_freight_rates.pluck(:shipping_line_id)
#     service_provider_id_hash = {}
#     organisation_ids = []
#     data.each do |object|
#         if object[:booking_params][:rate_card].present? && object[:booking_params][:rate_card][:service_rates].present?
#         object[:booking_params][:rate_card][:service_rates].each do |key, value|
#             service_provider_id_hash[key.to_sym] = value[:service_provider_id]
#             organisation_ids << value[:service_provider_id]
#         end
#         end
#     end
#     organisation_ids += data.pluck(:performed_by_org_id).uniq

#     objects = [
#         {
#         name: 'user',
#         filters: { id: data.pluck(:performed_by_id).concat(data.pluck(:closed_by_id)).uniq },
#         fields: [:id, :name, :email, :mobile_country_code, :mobile_number]
#         },
#         {
#         name: 'location',
#         filters: { id: fcl_freight_rates.pluck(:origin_port_id, :destination_port_id).flatten.uniq },
#         fields: [:id, :name, :display_name, :port_code, :type]
#         },
#         {
#         name: 'operator',
#         filters: { id: shipping_line_ids },
#         fields: [:id, :business_name, :short_name, :logo_url]
#         },
#         {
#         name: 'organization',
#         filters: { id: organisation_ids.uniq },
#         fields: [:id, :business_name, :short_name],
#         extra_params: { add_service_objects_required: false }
#         }
#     ]
#     if spot_search_details_required
#         objects << {
#         name: 'spot_search',
#         filters: { id: data.pluck(:source_id).uniq },
#         fields: [:id, :importer_exporter_id, :importer_exporter, :service_details]
#         }
#     end
#     service_objects = GetMultipleServiceObjectsData.run!(objects: objects)

#     data.each do |object|
#         rate = fcl_freight_rate_mappings[object[:fcl_freight_rate_id]].to_h rescue nil
#         object[:performed_by] = service_objects[:user][object[:performed_by_id].to_sym] rescue nil
#         object[:closed_by] = service_objects[:user][object[:closed_by_id].to_sym] rescue nil
#         object[:origin_port] = service_objects[:location][rate[:origin_port_id].to_sym] rescue nil
#         object[:destination_port] = service_objects[:location][rate[:destination_port_id].to_sym] rescue nil
#         object[:preferred_detention_free_days] = object[:preferred_detention_free_days] rescue nil
#         object[:closing_remarks] = object[:closing_remarks] rescue nil
#         object[:container_size] = rate[:container_size] rescue nil
#         object[:container_type] = rate[:container_type] rescue nil
#         object[:commodity] = rate[:commodity] rescue nil
#         object[:shipping_line] = service_objects[:operator][rate[:shipping_line_id].to_sym] rescue nil
#         object[:organization] = service_objects[:organization][object[:performed_by_org_id].to_sym] rescue nil
#         object[:containers_count] = object[:booking_params][:containers_count] rescue nil
#         object[:bls_count] = object[:booking_params][:bls_count] rescue nil
#         object[:inco_term] = object[:booking_params][:inco_term] rescue nil
#         object[:price] = rate[:validities].select { |t| t[:id] == object[:validity_id] }.first.to_h[:price] rescue nil
#         object[:currency] = rate[:validities].select { |t| t[:id] == object[:validity_id] }.first.to_h[:currency] rescue nil
#         object[:preferred_shipping_line_ids].each { |id| object[:preferred_shipping_lines] = object[:preferred_shipping_lines].to_a + [service_objects[:operator][id.to_sym]] } rescue nil
#         object[:spot_search] = service_objects[:spot_search][object[:source_id].to_sym] rescue nil
#         if object[:booking_params][:rate_card].present? && object[:booking_params][:rate_card][:service_rates].present?
#         object[:booking_params][:rate_card][:service_rates].each do |_key, value|
#             value[:service_provider] = service_objects[:organization][value[:service_provider_id].to_sym] rescue nil
#         end
#         end
#     end
#     end


def get_pagination_data(query, page, page_limit):
    params = {
      'page': page,
      'total': ceil(query.count()/page_limit),
      'total_count': query.count(),
      'page_limit': page_limit
    }
    return params

def get_stats(query, is_stats_required, performed_by_id):
    if not is_stats_required:
        return {}

    query = query.unwhere(FclFreightRateFeedback.status)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(eval(method_name), query, performed_by_id) for method_name in ['get_total', 'get_total_closed_by_user', 'get_total_opened_by_user', 'get_status_count']]
        results = {}
        for future in futures:
            result = future.result()
            results.update(result)  #we don't need this update last line me hi ho jaa rha (once check)

    method_responses = result
    stats = {
      'total': method_responses['get_total'],
      'total_closed_by_user': method_responses['get_total_closed_by_user'],
      'total_opened_by_user': method_responses['get_total_opened_by_user'],
      'total_open': method_responses['get_status_count']['active'] if method_responses['get_status_count'] else 0,
      'total_closed': method_responses['get_status_count']['inactive'] if method_responses['get_status_count'] else 0
    }
    return { 'stats': stats }

def get_total(query):
    try:
        count = query.count()
    except:
        count = None
    return count

def get_total_closed_by_user(query, performed_by_id):
    count = query.where(FclFreightRateFeedback.status == 'inactive', FclFreightRateFeedback.closed_by_id == performed_by_id).count() or None
    return count

def get_total_opened_by_user(query, performed_by_id):
    count = query.where(FclFreightRateFeedback.status =='active', FclFreightRateFeedback.closed_by_id == performed_by_id).count() or None
    return count

def get_status_count(query):
    count = query.group_by(FclFreightRateFeedback.status).select(FclFreightRateFeedback.status, fn.COUNT(FclFreightRateFeedback.id)).execute() or None
    return count
