from micro_services.client import maps
from services.ftl_freight_rate.rate_estimators.ftl_freight_rate_estimator import FtlFreightEstimator
from services.ftl_freight_rate.interactions.list_trucks import list_trucks_data
from configs.ftl_freight_rate_constants import TRUCK_TYPES_MAPPING,PREDICTION_TRUCK_TYPES, EU_ZONE, TON_TO_POUND
from fastapi import HTTPException

def get_ftl_freight_rate(
    origin_location_id,
    destination_location_id,
    commodity: None,
    weight: None,
    truck_type: None,
    truck_body_type: None,
    trip_type
):

    ids = [origin_location_id, destination_location_id]
    location_data_mapping = get_location_data_mapping(ids)
    country_id = location_data_mapping[origin_location_id]['country_id']
    country_category = get_country_code(location_data_mapping,origin_location_id,destination_location_id)
    truck_and_commodity_data = get_truck_and_commodity_data(
        country_category,truck_type, weight,country_id,trip_type,commodity,truck_body_type
    )
    rate_estimator = FtlFreightEstimator(origin_location_id,destination_location_id,location_data_mapping,truck_and_commodity_data,country_category)
    return rate_estimator.estimate()

def get_truck_and_commodity_data(country_category,truck_type, weight,country_id,trip_type,commodity=None,truck_body_type = None):
    filters = {
        'country_id':country_id
    }

    truck_weight = get_truck_weight_according_to_country(country_category, weight)

    if truck_type:
        closest_truck_type = truck_type
        filters['truck_name'] = truck_type
    else:
        default_truck_type = ''
        for truck_type, weight_limit_data in TRUCK_TYPES_MAPPING[country_category].items():
            if truck_weight > weight_limit_data['lower_limit'] and truck_weight <= weight_limit_data['upper_limit']:
                default_truck_type = truck_type
                break
        filters['capacity_greater_equal_than'] = truck_weight
        filters['truck_type'] = default_truck_type
        sorted_truck_types = sorted(PREDICTION_TRUCK_TYPES.items(), key=lambda x: x[1]["weight"])

        for truck_type, truck_data in sorted_truck_types:
            if weight >= 35:
                closest_truck_type = 'open_body_22tyre_35ton'
                break
            if truck_data["weight"] >= weight:
                closest_truck_type = truck_type
                break


    trucks_data = list_trucks_data(filters, sort_by='capacity',sort_type='asc')['list']

    if trucks_data:
        truck_details = trucks_data[0]
    else:
        raise HTTPException(status_code=400, detail="Truck data for these parameters are not available")

    truck_and_commodity_data = get_additional_truck_and_commodity_data(truck_details,truck_body_type,truck_weight,commodity,trip_type, closest_truck_type)
    return truck_and_commodity_data


def get_location_data_mapping(ids: list):
    location_data = maps.list_locations({"filters": {"id": ids}})["list"]
    location_mapping = {}
    for data in location_data:
        location_mapping[data["id"]] = data
    return location_mapping

def get_country_code(location_data_mapping,origin_location_id,destination_location_id):
    origin_country_code = location_data_mapping[origin_location_id]['country_code']
    destination_country_code = location_data_mapping[destination_location_id]['country_code']

    origin_continent_id = location_data_mapping[origin_location_id]['continent_id']
    destination_continent_id = location_data_mapping[destination_location_id]['continent_id']
    if origin_country_code == 'IN' and destination_country_code == 'IN':
        return 'IN'
    elif origin_continent_id in EU_ZONE and destination_continent_id in EU_ZONE:
        return 'EU'
    elif origin_country_code == 'US' and destination_country_code == 'US':
        return 'US'
    elif origin_country_code == 'CN' and destination_country_code == 'CN':
        return 'CN'
    elif origin_country_code == 'VN' and destination_country_code == 'VN':
        return 'VN'
    return 'not_found'

def get_additional_truck_and_commodity_data(truck_details,truck_body_type,weight,commodity,trip_type,closest_truck_type):
    truck_and_commodity_data = {
        'truck_body_type':truck_body_type or truck_details['body_type'],
        'truck_type':truck_details["truck_type"],
        'mileage':truck_details["mileage"],
        'mileage_unit':truck_details["mileage_unit"],
        'weight':weight or truck_details["capacity"],
        'commodity':commodity,
        'trip_type':trip_type,
        'fuel_type':truck_details['fuel_type'],
        'truck_name' : closest_truck_type,
        'vehicle_weight' : truck_details["vehicle_weight"],
        'no_of_wheels' : truck_details["no_of_wheels"]
    }
    return truck_and_commodity_data

def get_truck_weight_according_to_country(country_code,weight):
    if not weight:
        return 0
    if country_code == 'IN':
        return weight
    if country_code == 'US':
        return weight * TON_TO_POUND
    if country_code == 'EU':
        return weight
    if country_code == 'CN':
        return weight
    if country_code == 'VN':
        return weight
