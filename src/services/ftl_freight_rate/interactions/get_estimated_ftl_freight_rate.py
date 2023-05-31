from micro_services.client import maps
from services.ftl_freight_rate.rate_estimators.ftl_freight_rate_estimator import FtlFreightEstimator
from services.ftl_freight_rate.interaction.list_trucks import list_trucks_data
from configs.ftl_freight_rate_constants import TRUCK_TYPES_MAPPING

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
    truck_and_commodity_data = get_truck_and_commodity_data(
        truck_type, weight,country_id,trip_type,commodity,truck_body_type
    )
    rate_estimator = FtlFreightEstimator(origin_location_id,destination_location_id,location_data_mapping,truck_and_commodity_data)
    return rate_estimator.estimate()

def get_truck_and_commodity_data(truck_type, weight,country_id,trip_type,commodity=None,truck_body_type = None):
    data = {}
    filters = {
        'country_id':country_id
    }
    if truck_type:
        filters['truck_name'] = truck_type
    else:
        default_truck_type = ''
        for truck_type, weight_limit_data in TRUCK_TYPES_MAPPING.items():
            if weight >= weight_limit_data['lower_limit'] and weight <= weight_limit_data['upper_limit']:
                default_truck_type = truck_type
                break
        filters['capacity_greater_equal_than'] = weight
        filters['truck_type'] = default_truck_type

    truck_details = list_trucks_data(filters, sort_by='capacity',sort_type='asc')['list'][0]
    data['truck_body_type'] = truck_body_type or truck_details['body_type']
    data["truck_type"] = truck_details["truck_type"]
    data["mileage"] = truck_details["mileage"]
    data["mileage_unit"] = truck_details["mileage_unit"]
    data["weight"] = weight or truck_details["capacity"]
    data['commodity'] = commodity
    data['trip_type'] = trip_type
    data['fuel_type'] = truck_details['fuel_type']
    return data


def get_location_data_mapping(ids: list):
    location_data = maps.list_locations({"filters": {"id": ids}})["list"]
    location_mapping = {}
    for data in location_data:
        location_mapping[data["id"]] = data
    return location_mapping
