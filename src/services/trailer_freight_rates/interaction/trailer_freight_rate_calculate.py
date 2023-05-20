from services.trailer_freight_rates.models.trailer_freight_rate_constant import TrailerFreightRateCharges
from services.trailer_freight_rates.models.basic_trailer_rates import BasicTrailerRate
from services.envision.interaction.get_haulage_freight_predicted_rate import fuel_consumption
from fastapi import HTTPException
from database.db_session import db
from micro_services.client import maps
from libs.get_distance import get_distance
from playhouse.shortcuts import model_to_dict
from configs.trailer_freight_rate_constants import *
from services.trailer_freight_rates.models.trailer_freight_rate import TrailerFreightRate

def calculate_trailer_rate(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    from celery_worker import build_trailer_freight_rate_delay

    origin_location_id = request.get('origin_location_id')
    destination_location_id = request.get('destination_location_id')
    container_type = request.get('container_type')
    container_size = request.get('container_size')
    cargo_weight_per_container = request.get('cargo_weight_per_container') if request.get('cargo_weight_per_container') is not None else DEFAULT_MAX_WEIGHT_LIMIT.get(container_size)
    containers_count = request.get('containers_count')
    commodity = request.get('commodity')

    # path_data = get_path_from_valhala(origin_location_id, destination_location_id)
    # location_data = path_data["set_of_location"]
    # total_path_distance = path_data['total_distance']
    # average_fuel_price = get_average_fuel_price(location_data)
    input = {"filters":{"id":[origin_location_id, destination_location_id]}}
    data = maps.list_locations(input)
    if data:
        data = data["list"]
    else:
        raise HTTPException(status_code=404, detail="Location data not found")
    for d in data:
        if d["id"] == origin_location_id:
            origin_location = (d["latitude"], d["longitude"])
            origin_country_id = d.get('country_id')
            origin_city_id = d.get('city_id')
            origin_country_code = d.get('country_code')
        if d["id"] == destination_location_id:
            destination_location = (d["latitude"], d["longitude"])
            destination_country_id = d.get('country_id')
            destination_city_id = d.get('city_id')
            destination_country_code = d.get('country_code')

    if origin_country_code!=destination_country_code:
        raise HTTPException(status_code=404, detail="Origin and destination country should be same")
    
    if origin_country_code and destination_country_code not in CALCULATION_COUNTRY_CODES:
        origin_country_code = destination_country_code = DEFAULT_CALCULATION_COUNTRY_CODE

    try:
        distance = get_distance(origin_location,destination_location)
    except:
        distance = 250
    distance = distance if distance > 100 else 100
    transit_time = (distance//250) * 24
    if transit_time == 0:
        transit_time = 12
    fuel_used = fuel_consumption(distance,cargo_weight_per_container)
    print("fuel_uesd", fuel_used)

    fuel_cost = fuel_used * DEFAULT_FUEL_PRICES[destination_country_code] #use fuel charge with currency
    print("fuel cost", fuel_cost)
    constants = TrailerFreightRateCharges.select().where(
                (TrailerFreightRateCharges.country_code == destination_country_code),
                (TrailerFreightRateCharges.status == 'active')).first()
    
    if constants:
        constants_data = model_to_dict(constants)
    else:
        constants = TrailerFreightRateCharges.select().where(
                (TrailerFreightRateCharges.country_code == DEFAULT_CALCULATION_COUNTRY_CODE),
                (TrailerFreightRateCharges.status == 'active')).first()
        constants_data = model_to_dict(constants)
    
    handling_rate = constants_data.get('handling')
    nh_toll_rate = constants_data.get('nh_toll')
    tyre_rate = constants_data.get('tyre')
    driver_rate = constants_data.get('driver')
    document_rate = constants_data.get('document')
    maintanance_rate = constants_data.get('maintanance')
    misc_rate = constants_data.get('misc')

    constants_cost = (handling_rate + nh_toll_rate + tyre_rate + driver_rate + document_rate + maintanance_rate + misc_rate) * distance
    total_cost = (fuel_cost + constants_cost) * CONTAINER_SIZE_FACTORS[container_size]

    if containers_count > 1:
        total_cost = total_cost * (containers_count-0.35)

    if container_type in ['refer', 'open_top', 'iso_tank']:
        total_cost = total_cost + (total_cost * 0.1)

    line_items_data = [{"code": "BAS", "unit": "per_truck", "price": total_cost, "remarks": [], "currency": constants_data.get('currency_code')}]
    create_params = {
        'origin_location_id': origin_location_id,
        'destination_location_id': destination_location_id,
        'origin_country_id': origin_country_id,
        'destination_country_id': destination_country_id,
        'distance': distance,
        'line_items': line_items_data,
        'container_size' : container_size,
        'container_type' : container_type,
        'commodity' : commodity,
        'containers_count' : containers_count, 
        'service_provider_id': DEFAULT_SERVICE_PROVIDER_ID,
        'origin_city_id': origin_city_id,
        'destination_city_id': destination_city_id,
        'transit_time': transit_time
    }
    build_trailer_freight_rate_delay.apply_async(kwargs={'create_params' : create_params}, queue='low')

    return{'list':[{
        'base_price' : total_cost,
        'currency' : constants_data.get('currency_code'),
        'distance' : distance,
        'transit_time' : transit_time}]
    }

def get_path_from_valhala(origin_location_id, destination_location_id):
    return {}

def get_average_fuel_price(path_data):
    # location_ids = []
    # location_types = ["city", "district", "region"]
    # for location_type in location_types:
    #     location_ids += map(lambda x: x[location_type]["id"], path_data)

    # location_ids = list(set(location_ids))
    # all_fuel_price = FuelData.select(FuelData.fuel_price, FuelData.fuel_unit).where(
    #     FuelData.location_id << location_ids,
    #     FuelData.location_type << location_types,
    #     FuelData.fuel_type == "diesel"
    # )
    # avg_fuel_price = 0.0
    # for location_data in path_data:
    #     for location_type in location_types:
    #         fuel_data = list(filter(
    #             lambda data: data["id"] == location_data[location_type]
    #             and data["type"] == location_type,
    #             all_fuel_price,
    #         ))
    #         if bool(fuel_data):
    #             break
    #     avg_fuel_price += fuel_data[0]["fuel_price"]

    # return avg_fuel_price / len(location_ids)
    return {}

def build_trailer_freight_rate(create_params):
   TrailerFreightRate.create(**create_params)
   return