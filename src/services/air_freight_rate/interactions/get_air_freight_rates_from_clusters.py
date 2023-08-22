from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from datetime import datetime,timedelta
from services.air_freight_rate.constants.air_freight_rate_constants import AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO,COGOXPRESS
from configs.env import DEFAULT_USER_ID
from configs.global_constants import SERVICE_PROVIDER_FF
import concurrent.futures
from services.air_freight_rate.interactions.create_air_freight_rate import create_air_freight_rate_data
from micro_services.client import maps
def get_air_freight_rates_from_clusters(request):
    request_locations = [request.get('origin_airport_id'),request.get('destination_airport_id')]
    base_airports = AirFreightLocationClusterMapping.select(AirFreightLocationClusterMapping.cluster_id,AirFreightLocationClusterMapping.location_id).where(
        AirFreightLocationClusterMapping.location_id << request_locations
    )


    origin_base_airport_id = None
    destination_base_airport_id = None
    for base in base_airports:
        if str(base.location_id) == request.get('origin_airport_id'):
            origin_base_airport_id = str(base.cluster_id.base_airport_id)
        else:
            destination_base_airport_id = str(base.cluster_id.base_airport_id)
    rate_params = create_params(request,origin_base_airport_id,destination_base_airport_id)
    if len(rate_params) ==0:
        return False
    with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
        futures = [executor.submit(create_air_freight_rate_data, param) for param in rate_params]
    return True

def create_params(request,origin_base_airport_id,destination_base_airport_id):
    critical_rates = AirFreightRate.select(
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
            AirFreightRate.importer_exporter_id,
            AirFreightRate.source,
            AirFreightRate.updated_at,
            AirFreightRate.surcharge.alias('freight_surcharge')
        ).where(
            AirFreightRate.origin_airport_id == origin_base_airport_id,
            AirFreightRate.destination_airport_id == destination_base_airport_id,
            AirFreightRate.commodity == request.get('commodity'),
            AirFreightRate.commodity_type == request.get('commodity_type'),
            AirFreightRate.commodity_sub_type == request.get('commodity_subtype'),
            ~(AirFreightRate.rate_not_available_entry),
            AirFreightRate.shipment_type == request.get('packing_type'),
            AirFreightRate.stacking_type == request.get('handling_type'),
            AirFreightRate.rate_type == "market_place",
            AirFreightRate.last_rate_available_date >= request['validity_start'],
            AirFreightRate.source != 'predicted',
            AirFreightRate.service_provider_id == SERVICE_PROVIDER_FF,
            ((AirFreightRate.importer_exporter_id == request['importer_exporter_id']) | (AirFreightRate.importer_exporter_id.is_null(True)))

        )
    create_params = []
    cogo_envision_id = DEFAULT_USER_ID
    critical_rates_count = critical_rates.count()
    if critical_rates_count==0:
        return create_params
    data = {
            'origin_airport_id': request.get('origin_airport_id'),
            'destination_airport_id': request.get('destination_airport_id')
        }
    servicealble_airlines = maps.get_airlines_for_route(data)['airline_ids']
    for critical_rate in critical_rates:
        if servicebility_check(str(critical_rate.airline_id),servicealble_airlines):
            for validity in critical_rate.validities:
                validity_start = datetime.strptime(validity['validity_start'],'%Y-%m-%d').date()
                validity_end = datetime.strptime(validity['validity_end'],'%Y-%m-%d').date()

                if validity_check(request,validity_start,validity_end) and weight_slab_check(request,validity['weight_slabs']):
                    params = {
                        'origin_airport_id' : request['origin_airport_id'],
                        'destination_airport_id' : request['destination_airport_id'],
                        'commodity' : request.get('commodity'),
                        'commodity_type' : request.get('commodity_type'),
                        'commodity_sub_type': request.get('commodity_subtype'),
                        'airline_id' : str(critical_rate.airline_id),
                        'operation_type' : 'passenger',
                        'density_category' : validity.get('density_category'),
                        'currency' : validity['weight_slabs'][0]['currency'],
                        'price_type' :critical_rate.price_type,
                        'service_provider_id' :COGOXPRESS,
                        'performed_by_id' : cogo_envision_id,
                        'procured_by_id' : cogo_envision_id,
                        'sourced_by_id' : cogo_envision_id,
                        'shipment_type': request.get('packing_type'),
                        'stacking_type'  : request.get('handling_type'),
                        'validity_start' : max(datetime.combine(validity_start,datetime.min.time()),datetime.combine(datetime.now().date(),datetime.min.time())-timedelta(days=15)),
                        'validity_end' : datetime.combine(validity_end,datetime.min.time()),
                        'weight_slabs' : validity['weight_slabs'],
                        'min_price' : validity['min_price'],
                        'length': 300,
                        'breadth': 300,
                        'height': 300,
                        'source' : 'rate_extension',
                        'rate_type': critical_rate.rate_type,
                        'importer_exporter_id':str(critical_rate.importer_exporter_id)
                        }

                    create_params.append(params)
                    break
    return create_params

def validity_check(requirements,validity_start,validity_end):
    if validity_start > requirements.get('validity_end').date() or validity_end < requirements.get('validity_start').date() or requirements.get('cargo_clearance_date') < validity_start or requirements.get('cargo_clearance_date') > validity_end:
        return False
    return True

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


def servicebility_check(airline_id,servicealble_airlines):
    if airline_id in servicealble_airlines:
        return True
    return False
