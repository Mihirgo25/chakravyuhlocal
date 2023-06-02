from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge

from playhouse.postgres_ext import *
from configs.air_freight_rate_constants import RATE_ENTITY_MAPPING
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_shipping_line
import pdb

def get_air_freight_rate_cards(request):
    if request['commodity'] =='general':
        request['commodity_subtype'] = 'all'
    
    if request['commodity'] == 'special_consideration' and not request.get('commodity_subtype'):
        raise HTTPException(status_code=400, detail="commodity_sub_type is required for special_consideration")

    freight_query = initialize_freight_query(request)
    pdb.set_trace()
    freight_rates = join_surcharges(freight_query)
    freight_rates = check_eligible_airlines(freight_rates)






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
        AirFreightRate.cogo_entity_id
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
    
        



def check_eligible_airlines(freight_rates):
    airline_ids = [freight_rate['airline_id'] for freight_rate in freight_rates]
    airlines = get_shipping_line(id=airline_ids)
    active_airlines_ids = [sl["id"] for sl in airlines if sl["status"] == "active"]
    freight_rates = [rate for rate in freight_rates if rate["shipping_line_id"] in active_airlines_ids]
    return freight_rates



def join_surcharges(freight_query):
    join_query = (AirFreightRateSurcharge
                  .select()
                  .join(AirFreightRate,
                        on=(AirFreightRateSurcharge.id == AirFreightRate.surcharge_id) &
                           (AirFreightRateSurcharge.is_line_items_error_messages_present == False),
                        join_type='LEFT OUTER'))
    
    freight_query = freight_query.join(join_query)
    pdb.set_trace()
    return freight_query 
   
def build_response_object(freight_query_result, request):

    response_object = {
      'airline_id': freight_query_result['airline_id'],
      'origin_airport_id': freight_query_result['origin_airport_id'],
      'destination_airport_id': freight_query_result['destination_airport_id'],
      'origin_country_id': freight_query_result['origin_country_id'],
      'destination_country_id': freight_query_result['destination_country_id'],
      'price_type': freight_query_result['price_type'],
      'service_provider_id': freight_query_result['service_provider_id'],
      'shipment_type': freight_query_result['shipment_type'],
      'stacking_type': freight_query_result['stacking_type'],
      'commodity_sub_type_code': request['commodity_sub_type_code'],
      'commodity': freight_query_result['commodity'],
      'commodity_sub_type': freight_query_result['commodity_sub_type'],
      'operation_type': freight_query_result['operation_type'],
      'source': freight_query_result['source'],
      'tags': [],
      'rate_id': freight_query_result['id']
    }
    add_freight_objects(freight_query_result, response_object, request)
    add_surcharge_object(freight_query_result, response_object, request)




def build_response_list(freight_rates, request):
    grouping = {}
    for freight_rate in freight_rates:
        # if freight_query_result['freight']['origin_main_port_id'] and freight_query_result['freight']['destination_main_port_id']:
        key = ':'.join([freight_rate['airline_id'], freight_rate['operation_type'], freight_rate['service_provider_id'] or "", freight_rate['price_type'] or ""])
       
        response_object = build_response_object(freight_rate, request)

        if response_object:
            grouping[key] = response_object

    return list(grouping.values())


def add_freight_objects(freight_query_result, response_object, request):
    response_object['freights'] = []

    additional_weight_rate = 0
    additional_weight_rate_currency = 'USD'
    if request['cargo_weight_per_container'] and (request['cargo_weight_per_container'] - (response_object['weight_limit'].get('free_limit',0))) > 0:
        for slab in (response_object['weight_limit'].get('slabs',[]) or []):
            if slab['upper_limit'] < request['cargo_weight_per_container']:
                continue
            
            additional_weight_rate = slab['price']
            additional_weight_rate_currency = slab['currency']
            break

    freight_validities = freight_query_result['validities']

    for freight_validity in freight_validities:
      freight_object = build_freight_object(freight_validity, additional_weight_rate, additional_weight_rate_currency, request)
      if not freight_object:
        continue

      response_object['freights'].append(freight_object)


    return (len(response_object['freights']) > 0)


def build_freight_object(freight_validity, additional_weight_rate, additional_weight_rate_currency, request):
    pass









    
    

