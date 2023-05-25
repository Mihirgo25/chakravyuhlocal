from fastapi import HTTPException
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from playhouse.postgres_ext import *
from configs.air_freight_rate_constants import RATE_ENTITY_MAPPING
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_shipping_line

def get_air_freight_rate_cards(request):
    if request['commodity'] =='general':
        request['commodity_subtype'] = 'all'
    
    if request['commodity'] == 'special_consideration' and not request.get('commodity_subtype'):
        raise HTTPException(status_code=400, detail="commodity_sub_type is required for special_consideration")

    freight_query = initialize_freight_query(request)
    freight_rates = jsonable_encoder(list(freight_query.dicts()))
    freight_rates = check_eligible_airlines(freight_rates)




def initialize_freight_query(requirements,prediction_required=True):
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
    AirFreightRate.origin_port_id == requirements.get('origin_airport_id'),
    AirFreightRate.destination_port_id == requirements.get('destination_airport_id'),
    AirFreightRate.commodity == requirements.get('commodity'),
    AirFreightRate.commodity_type == requirements.get('commodity_type'),
    AirFreightRate.commodity_sub_type == requirements.get('commodity_subtype'),
    ~AirFreightRate.rate_not_available_entry,
    AirFreightRate.handling_type == requirements.get('handling_type'),
    AirFreightRate.shipment_type == requirements.get('shipment_type'),
    ((AirFreightRate.importer_exporter_id == requirements.get('importer_exporter_id')) | (AirFreightRate.importer_exporter_id == None))
    )

    if requirements.get('commodity_subtype_code'):
        freight_query.commodity_sub_type == requirements.get('commodity_subtype_code')

    freight_query = freight_query.where(AirFreightRate.last_rate_available_date >= requirements['validity_start'])


    if not prediction_required:
        freight_query  = freight_query.where(((AirFreightRate.mode != 'predicted') | (AirFreightRate.mode.is_null(True))))
    
        rate_constant_mapping_key = requirements.get('cogo_entity_id')

    allow_entity_ids = None
    if rate_constant_mapping_key in RATE_ENTITY_MAPPING:
        allow_entity_ids = RATE_ENTITY_MAPPING[rate_constant_mapping_key]

    if allow_entity_ids:
        freight_query = freight_query.where(((AirFreightRate.cogo_entity_id << allow_entity_ids) | (AirFreightRate.cogo_entity_id.is_null(True))))

def check_eligible_airlines(freight_rates):
    airline_ids = [freight_rate['airline_id'] for freight_rate in freight_rates]
    airlines = get_shipping_line(id=airline_ids)
    active_airlines_ids = [sl["id"] for sl in airlines if sl["status"] == "active"]
    freight_rates = [rate for rate in freight_rates if rate["shipping_line_id"] in active_airlines_ids]
    return freight_rates


def build_response_list(freight_rates):
    return





    
    

