from micro_services.client import maps
from configs.ftl_freight_rate_constants import (TRUCK_TYPES_MILEAGE_MAPPING,TRUCK_TYPES_MAPPING)
from services.ftl_freight_rate.rate_estimators.ftl_freight_rate_estimator import FtlFreightEstimator


def get_ftl_freight_rate(
    origin_location_id,
    destination_location_id,
    commodity_type: None,
    commodity_weight: None,
    truck_type: None,
    truck_body_type: None,
    trip_type
):
    
    ids = [origin_location_id, destination_location_id]
    location_data_mapping = get_location_data_mapping(ids)
    truck_and_commodity_data = get_truck_and_commodity_data(
        truck_type, commodity_weight,commodity_type,truck_body_type,trip_type
    )
    rate_estimator = FtlFreightEstimator(origin_location_id,destination_location_id,location_data_mapping,truck_and_commodity_data)
    return rate_estimator.estimate()

def get_truck_and_commodity_data(truck_type, commodity_weight,commodity_type=None,truck_body_type = None,trip_type = 'one_way'):
    data = {}
    if truck_type:
        truck_details = TRUCK_TYPES_MAPPING[truck_type]
        data["truck_type"] = truck_details["truck_type"]
        data["mileage"] = truck_details["mileage"]
        data["mileage_unit"] = truck_details["mileage_unit"]
        data["commodity_weight"] = truck_details["weight"]
    else:
        for truck_type, truck_data in TRUCK_TYPES_MILEAGE_MAPPING.items():
            if (
                truck_data["weight_lower_limit"] < commodity_weight
                and commodity_weight <= truck_data["weight_upper_limit"]
            ):
                data = truck_data
                data["truck_type"] = truck_type
                break
    data['truck_body_type'] = truck_body_type
    data['commodity_type'] = commodity_type
    data['trip_type'] = trip_type
    return data


def get_location_data_mapping(ids: list):
    location_data = maps.list_locations({"filters": {"id": ids}})["list"]
    location_mapping = {}
    for data in location_data:
        location_mapping[data["id"]] = data
    return location_mapping


    