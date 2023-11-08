from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import FclFreightLocationClusterMapping
from fastapi.encoders import jsonable_encoder
from datetime import datetime, timedelta
import concurrent.futures
from configs.fcl_freight_rate_constants import DEFAULT_SERVICE_PROVIDER_ID
from configs.env import DEFAULT_USER_ID
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from database.rails_db import get_ff_mlo
import dateutil.parser as parser

def get_fcl_freight_rates_from_clusters(request, serviceable_shipping_lines):
    ff_mlo = get_ff_mlo()
        
    create_params = []
    
    for hash in serviceable_shipping_lines:
        if not hash.get('shipping_lines'):
            continue
        
        origin_port_id = hash.get('origin_main_port_id') or hash.get('origin_port_id')
        destination_port_id = hash.get('destination_main_port_id') or hash.get('destination_port_id')
        
        with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
            futures = [executor.submit(get_create_params, origin_port_id, destination_port_id, request, ff_mlo, hash['shipping_lines'])]
        create_params.extend(futures)

    for i in range(len(create_params)):
        create_params[i] = create_params[i].result()
    
    create_params = [sublist for list in create_params for sublist in list if sublist]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
        futures = [executor.submit(create_fcl_freight_rate_data, param) for param in create_params]

def get_create_params(origin_port_id, destination_port_id, request, ff_mlo, shipping_lines):
    is_origin_base_port = FclFreightLocationCluster.select().where(FclFreightLocationCluster.base_port_id == origin_port_id).exists()
    is_destination_base_port = FclFreightLocationCluster.select().where(FclFreightLocationCluster.base_port_id == destination_port_id).exists()
    
    origin_base_port_id = None
    destination_base_port_id = None
    if is_origin_base_port:
        origin_base_port_id = origin_port_id
    else:
        origin_cluster_location_object = FclFreightLocationCluster.select(FclFreightLocationCluster.base_port_id).join(FclFreightLocationClusterMapping).where(FclFreightLocationClusterMapping.location_id == origin_port_id).first()
        origin_base_port_id = str(origin_cluster_location_object.base_port_id)
        
    if is_destination_base_port:
        destination_base_port_id = destination_port_id
    else:
        destination_cluster_location_object = FclFreightLocationCluster.select(FclFreightLocationCluster.base_port_id).join(FclFreightLocationClusterMapping).where(FclFreightLocationClusterMapping.location_id == destination_port_id).first()
        destination_base_port_id = str(destination_cluster_location_object.base_port_id)

    critical_freight_rates_query = FclFreightRate.select(
        FclFreightRate.id,
        FclFreightRate.shipping_line_id,
        FclFreightRate.validities,
        FclFreightRate.weight_limit
    ).where(
        FclFreightRate.origin_port_id == origin_base_port_id,
        FclFreightRate.destination_port_id == destination_base_port_id,
        FclFreightRate.container_size == request['container_size'],
        FclFreightRate.container_type == request['container_type'],
        FclFreightRate.commodity == request['commodity'],
        FclFreightRate.service_provider_id.in_(ff_mlo),
        ~FclFreightRate.rate_not_available_entry,
        FclFreightRate.rate_type == "market_place",
        FclFreightRate.last_rate_available_date >= request['validity_start'],
        FclFreightRate.shipping_line_id.in_(shipping_lines)
    )
    
    
    critical_freight_rates = jsonable_encoder(list(critical_freight_rates_query.dicts()))
    
    create_params = []
    
    for rate in critical_freight_rates:
        param = {
            'origin_port_id': request['origin_port_id'],
            'destination_port_id': request['destination_port_id'],
            'origin_country_id':request['origin_country_id'],
            'destination_country_id':request['destination_country_id'],
            'container_size': request['container_size'],
            'container_type': request['container_type'],
            'commodity': request['commodity'] if request.get('commodity') else 'general',
            'shipping_line_id' : rate["shipping_line_id"],
            'weight_limit': rate["weight_limit"],
            'service_provider_id' : DEFAULT_SERVICE_PROVIDER_ID,
            'performed_by_id': DEFAULT_USER_ID,
            'procured_by_id': DEFAULT_USER_ID,
            'sourced_by_id': DEFAULT_USER_ID,
            'source': 'rate_extension',
            'mode': 'cluster_extension',
            'accuracy': 80,
            'extended_from_object_id': rate["id"]
        }
        
        if origin_port_id != request['origin_port_id']:
            param['origin_main_port_id'] = origin_port_id
    
        if destination_port_id != request['destination_port_id']:
            param['destination_main_port_id'] = destination_port_id
            
        for validity in rate["validities"]:
            param["validity_start"] = datetime.strptime(datetime.now().date().isoformat(),'%Y-%m-%d')
            param["validity_end"] = datetime.strptime((datetime.now() + timedelta(days = 3)).date().isoformat(),'%Y-%m-%d')
            param["schedule_type"] = validity["schedule_type"]
            param["payment_term"] = validity["payment_term"]
            param["line_items"] = validity["line_items"]
            create_params.append(param)
            
    return create_params
        
            
            
        