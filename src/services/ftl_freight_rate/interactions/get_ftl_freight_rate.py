from micro_services.client import maps
from fastapi import HTTPException
from configs.ftl_freight_rate_constants import *
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from configs.ftl_freight_rate_constants import *
# from services.ftl_freight_rate.models.fuel_data import FuelData
from playhouse import model_to_dict
from micro_services.client import maps



from services.ftl_freight_rate.models.ftl_freight_rate_rule_set import (
    FtlFreightRateRuleSet,
)
from playhouse.shortcuts import model_to_dict


def get_ftl_freight_rate(
    origin_location_id,
    destination_location_id,
    truck_type: None,
    truck_body_type:None,
    commodity_weight: None,
    commodity_type: None,
):
    if not truck_type or not commodity_weight:
        raise HTTPException(
            status_code=500, detail="either truck type or commodity_weight is required"
        )

    truck_and_commodity_data =  get_truck_and_commodity_data(truck_type,commodity_weight)
    if truck_type:
        truck_type = truck_and_commodity_data['truck_type']
    if commodity_weight:
        commodity_weight = truck_and_commodity_data['commodity_weight']
        
    ftl_freight_rate = list_ftl_freight_rate(
        origin_location_id,
        destination_location_id,
        truck_and_commodity_data['truck_type'],
        commodity_type,
        commodity_weight,
    )
    result = {}
    
    if ftl_freight_rate:
        return {"data": ftl_freight_rate}
    
    path_data = get_path_from_valhala(origin_location_id, destination_location_id)
    location_data = path_data["set_of_location"]
    total_path_distance = path_data['total_distance']
    average_fuel_price = get_average_fuel_price(location_data)
    applicable_rule_set = get_applicable_rule_set(origin_location_id,destination_location_id,truck_and_commodity_data)
    basic_freight_charges = average_fuel_price*total_path_distance
    for data in applicable_rule_set:
        if data['process_type'] in BASIC_CHARGE_LIST:
            if data['process_unit'] == 'km': 
                basic_freight_charges += (data['process_val']*total_path_distance)
            else:
                basic_freight_charges += (data['process_val']*total_path_distance*0.621371)
    
    if commodity_type in HAZ_CLASSES:
        basic_freight_charges += 0.1*basic_freight_charges
    
    result["base_rate"] = basic_freight_charges
    result["distance"] = total_path_distance
    return result
    
def list_ftl_freight_rate(
    origin_location_id,
    destination_location_id,
    truck_type,
    commodity_type: None,
    truck_body_type: None,
):
    ftl_freight_rate = FtlFreightRate.select().where(
        origin_location_id=origin_location_id,
        destination_location_id=destination_location_id,
        truck_type=truck_type,
        truck_body_type = truck_body_type,
        commodity_type=commodity_type,
    )
    return model_to_dict(ftl_freight_rate)


def get_path_from_valhala(origin_location_id, destination_location_id):
    return {}


def get_applicable_rule_set(origin_location_id, destination_location_id,truck_and_commodity_data):
    location_mapping = {}
    ids = [origin_location_id, destination_location_id]
    truck_type = truck_and_commodity_data['truck_type']
    location_data = maps.list_locations({'filters': {'id': ids}})
    
    for data in location_data:
        location_mapping[data['id']] = data['country_id']
        
    ftl_freight_rate_rule_set = FtlFreightRateRuleSet.select().where(
            FtlFreightRateRuleSet.location_id
            << list(
                location_mapping[origin_location_id],
                location_mapping[destination_location_id],
            ),
            FtlFreightRateRuleSet.location_type == 'country',
            FtlFreightRateRuleSet.truck_type == truck_type
        ).dicts()
    return ftl_freight_rate_rule_set


def get_average_fuel_price(path_data):
    location_ids = []
    location_types = ["city", "district", "region"]
    for location_type in location_types:
        location_ids += map(lambda x: x[location_type]["id"], path_data)

    location_ids = list(set(location_ids))
    all_fuel_price = FuelData.select(FuelData.fuel_price, FuelData.fuel_unit).where(
        FuelData.location_id << location_ids,
        FuelData.location_type << location_types,
        FuelData.fuel_type == "diesel"
    )
    avg_fuel_price = 0.0
    for location_data in path_data:
        for location_type in location_types:
            fuel_data = list(filter(
                lambda data: data["id"] == location_data[location_type]
                and data["type"] == location_type,
                all_fuel_price,
            ))
            if bool(fuel_data):
                break
        avg_fuel_price += fuel_data[0]["fuel_price"]

    return avg_fuel_price / len(location_ids)

def get_truck_and_commodity_data(truck_type, commodity_weight):
    data = {}
    if truck_type:
        truck_details = TRUCK_TYPES_MAPPING[truck_type]
        data['truck_type'] = truck_details['truck_type']
        data['mileage'] = truck_details['mileage']
        data['mileage_unit'] = truck_details['mileage_unit']
        data['commodity_weight'] = truck_details['weight']
    else:
        for truck_type,truck_data in TRUCK_TYPES_MILEAGE_MAPPING.items():
            if truck_data['weight_lower_limit'] <= commodity_weight and  commodity_weight <= truck_data['weight_upper_limit']:
                data = truck_data
                data['truck_type'] = truck_type
                break
            
    return data
