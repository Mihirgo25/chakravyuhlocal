from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from playhouse.postgres_ext import *
from configs.air_freight_rate_constants import RATE_ENTITY_MAPPING,AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO,MAX_CARGO_LIMIT,DEFAULT_SERVICE_PROVIDER_ID
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_shipping_line
import pdb
from database.rails_db import get_eligible_orgs
from configs.definitions import AIR_FREIGHT_SURCHARGES
from services.air_freight_rate.interaction.get_air_freight_rate_prediction import get_air_freight_rate_prediction
from services.air_freight_rate.helpers.air_freight_rate_card_helper import get_density_wise_rate_card

def initialize_freight_query(requirements,prediction_required=False):
    freight_query = AirFreightRate.select(
        AirFreightRate.id,
        AirFreightRate.airline_id,
        AirFreightRate.origin_airport_id,
        AirFreightRate.destination_airport_id,
        AirFreightRate.origin_country_id,
        AirFreightRate.destination_country_id,
        AirFreightRate.operation_type,
        AirFreightRate.commodity,
        AirFreightRate.commodity_type,
        AirFreightRate.commodity_sub_type,
        AirFreightRate.stacking_type,
        AirFreightRate.shipment_type,
        AirFreightRate.validities,
        AirFreightRate.price_type,
        AirFreightRate.service_provider_id,
        AirFreightRate.cogo_entity_id,
        AirFreightRate.surcharge.alias('freight_surcharge')
    ).where(
    AirFreightRate.origin_airport_id == requirements.get('origin_airport_id'),
    AirFreightRate.destination_airport_id == requirements.get('destination_airport_id'),
    AirFreightRate.commodity == requirements.get('commodity'),
    AirFreightRate.commodity_type == requirements.get('commodity_type'),
    AirFreightRate.commodity_sub_type == requirements.get('commodity_subtype'),
    AirFreightRate.rate_not_available_entry==False,
    AirFreightRate.shipment_type == requirements.get('packing_type'),
    AirFreightRate.stacking_type == requirements.get('handling_type'),
    )
    rate_constant_mapping_key = requirements.get('cogo_entity_id')

    allowed_entity_ids = None
    if rate_constant_mapping_key in RATE_ENTITY_MAPPING:
        allowed_entity_ids = RATE_ENTITY_MAPPING[rate_constant_mapping_key]

    if allowed_entity_ids:
        freight_query = freight_query.where(((AirFreightRate.cogo_entity_id << allowed_entity_ids) | (AirFreightRate.cogo_entity_id.is_null(True))))

    if requirements.get('commodity_subtype_code'):
        freight_query.commodity_sub_type == requirements.get('commodity_subtype_code')

    freight_query = freight_query.where(AirFreightRate.last_rate_available_date >= requirements['validity_start'])


    if not prediction_required:
        freight_query  = freight_query.where(((AirFreightRate.source != 'predicted') | (AirFreightRate.source.is_null(True))))

    return freight_query


def build_response_object(freight_rate,requirements,is_predicted):
    source = 'spot_rates'
    if freight_rate['mode'] == 'predicted':
        source = 'predicted'

    response_object = {
        'airline_id': freight_rate['airline_id'],
        'origin_airport_id': freight_rate['origin_airport_id'],
        'destination_airport_id': freight_rate['destination_airport_id'],
        'origin_country_id': freight_rate['origin_country_id'],
        'destination_country_id': freight_rate['destination_country_id'],
        'operation_type': freight_rate['operation_type'],
        'commodity': freight_rate['commodity'],
        'commodity_type': freight_rate['commodity_type'],
        'commodity_sub_type': freight_rate['commodity_sub_type'],
        'stacking_type': freight_rate['stacking_type'],
        'shipment_type': freight_rate['shipment_type'],
        'price_type': freight_rate['price_type'],
        'service_provider_id': freight_rate['service_provider_id'],
        'source': source,
        'rate_id': freight_rate['id'],
        'cogo_entity_id': freight_rate['cogo_entity_id']
    }
    add_freight_objects(freight_rate,response_object,requirements)

    add_surcharge_object(freight_rate,response_object,requirements)

    if not is_predicted:
        response_object = get_density_wise_rate_card(response_object, freight_rate['trade_type'], freight_rate['weight'], freight_rate['volume'], get_chargeable_weight) 

    return response_object

def add_surcharge_object(freight_rate,response_object,requirements):
    if freight_rate['freight']['price'] == 'all_in':
        return True
    response_object['surcharge'] = {
        'line_items':[]
    }

    line_items = freight_rate['freight_surcharge']['line_items']

    for line_item in line_items:
        line_item = build_surcharge_line_item_object(line_item,requirements)
        if not line_item:
            return 
        response_object['surcharge']['line_items'].append(line_item)
    
    return True

def build_surcharge_line_item_object(line_item,requirements):
    surcharge_charges = AIR_FREIGHT_SURCHARGES

    line_item = {key:val for key,val in line_item.items() if key in ['code','price','min_price','currency','remarks','unit']}

    if line_item.get('unit') == 'per_package':
        line_item['quantity'] = requirements.get('packages_count')
    elif line_item.get('unit') == 'per_kg':
        line_item['quantity'] = get_chargeable_weight(requirements)
    else:
        line_item['quantity'] = 1
    
    line_item['total_price'] = line_item['quantity']*line_item['price']
    if line_item['min_price'] > line_item['total_price']:
        line_item['total_price'] = line_item['min_price']
    line_item['name'] = surcharge_charges[line_item['code']]['name']
    line_item['source'] = 'system'

    return line_item

def build_response_list(freight_rates, requirements,is_predicted):
    grouping = {}
    for freight_rate in freight_rates:
        key = ':'.join([freight_rate['airline_id'], freight_rate['operation_type'], freight_rate['service_provider_id'] or "", freight_rate['price_type'] or ""])
        response_object = build_response_object(freight_rate, requirements,is_predicted)

        if response_object:
            grouping[key] = response_object

    return list(grouping.values())

def get_chargeable_weight(requirements):
    volumetric_weight = requirements.get('volume') * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
    if volumetric_weight > requirements.get('weight'):
        chargeable_weight = volumetric_weight
    else:
        chargeable_weight = requirements.get('weight')

    return chargeable_weight


def add_freight_objects(freight_query_result, response_object, requirements):
    response_object['freights'] = []
    freight_validities = freight_query_result['validities']
    required_weight = get_chargeable_weight(requirements)

    for freight_validity in freight_validities:
        freight_object = build_freight_object(freight_validity,required_weight,requirements)
        if not freight_object:
            continue
        response_object['freights'].append(freight_object)
    
    return True

def build_freight_object(freight_validity,required_weight,requirements):
    freight_validity['density_category'] = freight_validity['density_category'] if  freight_validity.get('density_category') else 'general'
    freight_validity['min_density_weight'] = freight_validity['min_density_weight'] if  freight_validity.get('min_density_weight') else 0.01
    freight_validity['max_density_weight'] = freight_validity['max_density_weight'] if  freight_validity.get('max_density_weight') else MAX_CARGO_LIMIT

    if freight_validity['validity_start'] > requirements.get('validity_end') or freight_validity['validity_end'] < requirements.get('validity_start') or requirements.get('cargo_clearance_date') < freight_validity.get('validity_start') or requirements.get('cargo_clearance_date') > freight_validity['validity_end'] or not freight_validity['status']:
        return
    
    freight_object = {
        'validity_start' : freight_validity['validity_start'],
        'validity_end': freight_validity['validity_end'],
        'validity_id': freight_validity['id'],
        'likes_count': freight_validity['likes_count'],
        'dislikes_count': freight_validity['dislikes_count'],
        'density_category': freight_validity['density_category'],
        'min_density_weight': freight_validity['min_density_weight'],
        'max_density_weight': freight_validity['max_density_weight'],
        'line_items': []
        }
    
    if requirements.get('validity_start') > freight_validity['validity_start']:
        freight_object['validity_start'] = requirements['validity_start']
    
    if requirements.get('validity_end') < freight_validity['validity_end']:
        freight_object['validity_end'] = requirements['validity_end'] 

    weight_slabs = freight_validity['weight_slabs']
    required_slab = None

    for weight_slab in weight_slabs:
        if required_weight >= int(weight_slab['lower_limit']) and required_weight < weight_slab['upper_limit']:
            required_slab = weight_slab
            break
    
    if not required_slab:
        return
    
    if required_weight <= 500:
        required_next_slab = None
        for weight_slab in weight_slabs:
            if (required_slab['upper_limit'] + 1)  <= int(weight_slab['lower_limit']) and required_weight < weight_slab['upper_limit']:
                required_next_slab = weight_slab
                break
        
        if required_next_slab:
            lower_rate = required_next_slab['tariff_price']
            higher_rate = required_slab['tariff_price']

            break_even_weight = (required_next_slab['lower_limit'] * lower_rate) / higher_rate
            if required_weight >= break_even_weight:
                required_slab = required_next_slab
    
    price = round(required_slab['tariff_price'],2)
    min_price = freight_validity['min_price']
    currency = freight_validity['currency']
    line_item = { 'code': 'BAS', 'unit': 'per_kg', 'price': price, 'currency': currency, 'min_price': min_price, 'remarks': [] }
    #  code name from charges but not required as there only one line item
    if line_item.get('unit') == 'per_package':
        line_item['quantity'] = requirements.get('packages_count')
    elif line_item.get('unit') == 'per_kg':
        line_item['quantity'] = required_weight
    else:
        line_item['quantity'] = 1
    
    line_item['total_price'] = line_item['quantity']*line_item['price']
    if line_item['min_price'] > line_item['total_price']:
        line_item['total_price'] = line_item['min_price']
    line_item['name'] = 'Basic Freight'
    line_item['source'] = 'system'
    freight_object['line_items'].append(line_item)
    return freight_object



def is_missing_surcharge(freight_rate):
    return not freight_rate['surcharge'] or 'line_items' not in freight_rate['surcharge'] or len(freight_rate['surcharge']['line_items']) == 0 or freight_rate["is_surcharge_line_items_error_messages_present"]

def get_missing_surcharges(freight_rates):
    missing_surcharges = []
    for freight_rate in freight_rates:
        if is_missing_surcharge(freight_rate):
            missing_surcharges.append(freight_rate)
    
    return missing_surcharges

def get_surcharges(requirements,rates):
    airline_ids = []
    service_provider_ids = []

    for rate in rates:
        if rate["service_provider_id"]:
            service_provider_ids.append(rate['service_provider_id'])
        airline_ids.append(rate['airline_id'])
    
    surcharges_query = AirFreightRateSurcharge.select(
        AirFreightRateSurcharge.line_items,
        AirFreightRateSurcharge.airline_id,
        AirFreightRateSurcharge.service_provider_id
    ).where(
        AirFreightRateSurcharge.origin_airport_id == requirements['origin_airport_id'],
        AirFreightRateSurcharge.destination_airport_id == requirements['destination_airport_id'],
        AirFreightRateSurcharge.commodity == requirements['commodity'],
        AirFreightRateSurcharge.operation_type == requirements['operation_type'],
        AirFreightRateSurcharge.airline_id << airline_ids,
        AirFreightRateSurcharge.service_provider_id << service_provider_ids
    )

    surcharges_results = jsonable_encoder(list(surcharges_query.dicts()))
    # formated_surchages = []
    # for surcharge in surcharges_results:

    return surcharges_results


def discard_noneligible_airlines(freight_rates):
    airline_ids = [rate["airline_id"] for rate in freight_rates]
    airlines = get_shipping_line(id=airline_ids,operator_type = 'airline')
    active_airline_ids = [airline["id"] for airline in airlines if airline["status"] == "active"]
    freight_rates = [rate for rate in freight_rates if rate["airline_id"] in active_airline_ids]
    return freight_rates

def get_matching_surchages(freight_rate,surcharges):
    for surcharge in surcharges:
        if surcharge['airline_id'] == freight_rate['airline_id'] and surcharge['service_provider_id'] == freight_rate['service_provider_id']:
            return {'line_items':surcharge['line_items']}  
    return None

def fill_missing_surcharges(freight_rates,surcharges):
    new_freight_rates = []
    for freight_rate in freight_rates:
        if is_missing_surcharge(freight_rate):
            freight_rate['freight_surcharge'] = get_matching_surchages(freight_rate,surcharges)
        new_freight_rates.append(freight_rate)
    
    return new_freight_rates

def discard_noneligible_lsps(freight_rates):
    ids = get_eligible_orgs('air_freight')

    freight_rates = [rate for rate in freight_rates if rate["service_provider_id"] in ids]
    return freight_rates

def pre_discard_noneligible_rates(freight_rates):
    if len(freight_rates) > 0:
        freight_rates = discard_noneligible_lsps(freight_rates)
    if len(freight_rates) > 0:
        freight_rates = discard_noneligible_airlines(freight_rates)
    return freight_rates

def remove_cogoxpress_service_provider(list):
    airline_wise_list = {}
    for rate in list:
        airline_id = rate['airline_id']
        if airline_id not in airline_wise_list:
            airline_wise_list[airline_id] = []
        airline_wise_list[airline_id].append(rate)
    
    new_list = []
    for _, rate_list in airline_wise_list.items():
        more_service_providers = len(set([r['service_provider_id'] for r in rate_list if r['service_provider_id'] is not None])) > 1
        for new_rate in rate_list:
            if more_service_providers and new_rate['service_provider_id'] == DEFAULT_SERVICE_PROVIDER_ID:
                continue
            new_list.append(new_rate)
    
    return new_list


def get_air_freight_rate_cards(requirements):
    if requirements['commodity'] =='general':
        requirements['commodity_subtype'] = 'all'
    
    if requirements['commodity'] == 'special_consideration' and not requirements.get('commodity_subtype'):
        raise HTTPException(status_code=400, detail="commodity_sub_type is required for special_consideration")
    freight_query = initialize_freight_query(requirements)
    freight_rates = jsonable_encoder(list(freight_query.dicts()))
    freight_rates = remove_cogoxpress_service_provider(freight_rates)
    is_predicted = False

    if len(freight_rates)==0:
        get_air_freight_rate_prediction(requirements)
        is_predicted = True
        freight_rates = initialize_freight_query(requirements)
        freight_rates = jsonable_encoder(list(freight_rates.dicts()),True)
    
    freight_rates = pre_discard_noneligible_rates(freight_rates, requirements)
    surcharges = get_missing_surcharges(freight_rates)
    freight_rates = fill_missing_surcharges(freight_rates,surcharges)
    freight_rates = build_response_list(freight_rates,requirements,is_predicted)

    return {
        'list':list
    }

   
            



# NOT USED

#   def add_storage_objects(freight_query_result, response_object)
#     response_object[:origin_storage] = freight_query_result[:origin_storage].merge({ unit: 'per_kg_per_day' })
#     response_object[:destination_storage] = freight_query_result[:destination_storage].merge({ unit: 'per_kg_per_day' })

#     return true
#   end












    
    

