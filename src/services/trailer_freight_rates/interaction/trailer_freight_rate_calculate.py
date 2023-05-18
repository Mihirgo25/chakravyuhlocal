from services.trailer_freight_rates.models.trailer_freight_rate_constant import TrailerFreightRateCharges
from services.trailer_freight_rates.models.basic_trailer_rates import BasicTrailerRate
from services.envision.interaction.get_haulage_freight_predicted_rate import fuel_consumption
from fastapi import HTTPException
from database.db_session import db
from micro_services.client import maps
from libs.get_distance import get_distance
from playhouse.shortcuts import model_to_dict
from configs.trailer_freight_rate_constants import *

def calculate_trailer_rate(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):

    origin_location_id = request.get('origin_location_id')
    destination_location_id = request.get('destination_location_id')
    container_size = request.get('container_size')
    cargo_weight_per_container = request.get('cargo_weight_per_container') if request.get('cargo_weight_per_container') is not None else DEFAULT_MAX_WEIGHT_LIMIT.get(container_size)
    # basic_rate = BasicTrailerRate.select().where(
    #             (BasicTrailerRate.container_size == container_size),
    #             (BasicTrailerRate.container_type == request["container_type"]),
    #             (BasicTrailerRate.origin_location_id == origin_location_id),
    #             (BasicTrailerRate.destination_location_id == destination_location_id),
    #             (BasicTrailerRate.cargo_weight_per_container == cargo_weight_per_container),
    #             (BasicTrailerRate.containers_count == request["containers_count"]),
    #             (BasicTrailerRate.status == 'active')
    #             ).first()

    # if basic_rate:
    #     print("yes")
    #     return {'base_rate' : basic_rate.base_rate, 
    #             'currency' : basic_rate.currency, 
    #             'distance' : basic_rate.distance,
    #             'transit_time' : basic_rate.transit_time
    #             }
        # raise HTTPException(status_code=404, detail="Data not found")

    input = {"filters":{"id":[origin_location_id, destination_location_id]}}
    data = maps.list_locations(input)
    if data:
        data = data["list"]
    else:
        raise HTTPException(status_code=404, detail="Location data not found")
    for d in data:
        if d["id"] == origin_location_id:
            origin_location = (d["latitude"], d["longitude"])
            origin_country_code = d.get('country_code')
        if d["id"] == destination_location_id:
            destination_location = (d["latitude"], d["longitude"])
            destination_country_code = d.get('country_code')

    if origin_country_code!=destination_country_code:
        raise HTTPException(status_code=404, detail="Origin and destination country should be same")
    
    if origin_country_code and destination_country_code not in CALCULATION_COUNTRY_CODES:
        origin_country_code = destination_country_code = DEFAULT_CALCULATION_COUNTRY_CODE

    # try:
    #     distance = get_distance(origin_location,destination_location)
    #     print("distance", distance)
    # except:
    distance = 10
    transit_time = (distance//250) * 24
    if transit_time == 0:
        transit_time = 12
    fuel_used = fuel_consumption(distance,cargo_weight_per_container)
    print("fuel_uesd", fuel_used)
    # fuel_charge = get_fuel_charge()
    fuel_cost = fuel_used * DEFAULT_FUEL_PRICES[destination_country_code] #use fuel charge with currency
    print("fuel cost", fuel_cost)
    constants = TrailerFreightRateCharges.select().where(
                (TrailerFreightRateCharges.country_code == destination_country_code),
                (TrailerFreightRateCharges.status == 'active')).first()
    
    if constants:
        constants_data = model_to_dict(constants)
    else:
        raise HTTPException(status_code=404, detail="Constants data not found")
    
    handling_rate = constants_data.get('handling')
    nh_toll_rate = constants_data.get('nh_toll')
    tyre_rate = constants_data.get('tyre')
    driver_rate = constants_data.get('driver')
    document_rate = constants_data.get('document')
    maintanance_rate = constants_data.get('maintanance')
    misc_rate = constants_data.get('misc')

    constants_cost = (handling_rate + nh_toll_rate + tyre_rate + driver_rate + document_rate + maintanance_rate + misc_rate) * distance
    print("constant cost", constants_cost)
    if request.get('containers_count')==1:
        total_cost = fuel_cost + constants_cost
    else:
        total_cost = (fuel_cost + constants_cost) * (request.get('containers_count')-0.3)
    print("total_cost",total_cost)

    row = {
        'container_size' : request.get('container_size'),
        'container_type' : request.get('container_type'),
        'trailer_type' : request.get('trailer_type'),
        'commodity' : request.get('commodity'),
        'origin_location_id' : request.get('origin_location_id'),
        'destination_location_id' : request.get('destination_location_id'),
        'base_rate' : total_cost,
        'currency' : constants_data.get('currency_code'),
        'distance' : distance,
        'cargo_weight_per_container' : cargo_weight_per_container,
        'country_code' : destination_country_code,
        'containers_count' : request.get('containers_count'),
        'transit_time' : transit_time
    }
    basic_rate = BasicTrailerRate.create(**row)

    if not basic_rate.save():
        raise HTTPException(status_code=500, detail="Base rate not saved")
    
    return {'base_rate' : basic_rate.base_rate,
            'currency' : basic_rate.currency,
            'distance' : basic_rate.distance,
            'transit_time' : transit_time}