from fastapi.encoders import jsonable_encoder
from services.air_freight_rate.interactions.create_air_freight_rate import create_air_freight_rate
from datetime import datetime, timedelta
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.constants.air_freight_rate_constants import DEFAULT_RATE_TYPE, COGOXPRESS, AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
from configs.env import DEFAULT_USER_ID
import concurrent.futures



def get_near_expire_rates(requirements):
    from services.air_freight_rate.interactions.get_air_freight_rate_cards import initialize_freight_query, pre_discard_noneligible_rates, remove_cogoxpress_service_provider, valid_weight_slabs
    freight_rates = []
    freight_query = initialize_freight_query(requirements = requirements, near_expired_rates = True)
    freight_rates = jsonable_encoder(list(freight_query.dicts()))
    freight_rates = pre_discard_noneligible_rates(freight_rates)
    freight_rates = remove_cogoxpress_service_provider(freight_rates)
    valid_freight_rates =  build_create_params(freight_rates, requirements)
    expired_ids = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        expired_ids = list(executor.map(create_rate_and_get_id, valid_freight_rates))
    freight_rates = get_freight_data(jsonable_encoder(expired_ids))
    return freight_rates



def create_rate_and_get_id(rate):
    rate = create_air_freight_rate(rate)
    return rate['id']

def build_create_params(freight_rates, requirements):
    from services.air_freight_rate.interactions.get_air_freight_rate_cards import valid_weight_slabs
    valid_freight_rates = []

    for freight_rate in freight_rates:
        validities = freight_rate['validities'][-1]
        if weight_slab_check(requirements,validities['weight_slabs']):
            valid_freight_rates.append(get_create_params(freight_rate, validities))
    return valid_freight_rates

def get_create_params(rate, validity):
    data ={
        'origin_airport_id' : rate['origin_airport_id'],
        'destination_airport_id' : rate['destination_airport_id'],
        'commodity' : rate.get('commodity'),
        'commodity_type' : rate.get('commodity_type'),
        'commodity_sub_type': rate.get('commodity_subtype'),
        'airline_id' : rate['airline_id'],
        'operation_type' : rate['operation_type'],
        'density_category' : validity['density_category'],
        'currency' : validity['currency'],
        'price_type' :rate['price_type'], 
        'service_provider_id' :COGOXPRESS,
        'performed_by_id' : DEFAULT_USER_ID,
        'procured_by_id' : DEFAULT_USER_ID,
        'sourced_by_id' : DEFAULT_USER_ID,
        'shipment_type': rate.get('shipment_type'),
        'stacking_type'  : rate.get('stacking_type'),
        'validity_start' : (datetime.now()),
        'validity_end' : (datetime.now() + timedelta(days=2)),
        'cargo_clearance_date': datetime.strptime(datetime.now().date().isoformat(),'%Y-%m-%d'),
        'length': 300,
        'breadth': 300,
        'height': 300,
        'source' : 'expired_extention',
        'rate_type': DEFAULT_RATE_TYPE,
        'weight_slabs': validity['weight_slabs'],
        'min_price': validity['min_price'],
    }
    return data

def get_freight_data(ids):
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
        AirFreightRate.rate_type,
        AirFreightRate.service_provider_id,
        AirFreightRate.cogo_entity_id,
        AirFreightRate.source,
        AirFreightRate.updated_at,
        AirFreightRate.importer_exporter_id,
        AirFreightRate.surcharge.alias('freight_surcharge')
    ).where(AirFreightRate.id << ids)

    return jsonable_encoder(list(freight_query.dicts()))


def weight_slab_check(request,weight_slabs):
    chargeable_weight = get_chargeable_weight(request)
    for weight_slab in weight_slabs:
        if chargeable_weight >= int(weight_slab['lower_limit']) and chargeable_weight < weight_slab['upper_limit']:
            return True
    return False


def get_chargeable_weight(requirements):
    volumetric_weight = requirements.get('volume') * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
    if volumetric_weight > requirements.get('weight'):
        chargeable_weight = volumetric_weight
    else:
        chargeable_weight = requirements.get('weight')

    return chargeable_weight