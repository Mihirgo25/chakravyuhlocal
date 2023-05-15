from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet
from services.haulage_freight_rate.models.wagon_types import WagonTypes
import geopy.distance
from micro_services.client import maps
import services.haulage_freight_rate.interactions.rate_calculator as rate_calculator
from configs.rails_constants import DEFAULT_PERMISSIBLE_CARRYING_CAPACITY
from configs.rails_constants import DESTINATION_TERMINAL_CHARGES_INDIA


POSSIBLE_LOCATION_CATEGORY = ["india", "china", "europe", "north_america"]


def get_distance(origin_location, destination_location, data):
    for d in data:
        if d["id"] == origin_location:
            origin_location = (d["latitude"], d["longitude"])
        if d["id"] == destination_location:
            destination_location = (d["latitude"], d["longitude"])
    coords_1 = origin_location
    coords_2 = destination_location
    return geopy.distance.geodesic(coords_1, coords_2).km


def haulage_rate_calculator(
    origin_location,
    destination_location,
    commodity,
    load_type=None,
    container_count=None,
    wagon_type=None
):
    response = {"success": False, "status_code": 200}
    #check country
    input = {"filters": {"id": [origin_location, destination_location]}}
    location_category = ''
    data = maps.list_locations(input)['list']
    if data[0]['country_code'] == 'IN' and data[0]['country_code'] == 'IN':
        location_category = 'india'
    if location_category not in POSSIBLE_LOCATION_CATEGORY:
        return response
    #check intermodal


    ports_distance = get_distance(origin_location, destination_location, data)

    if not container_count:
        load_type = "Wagon Load"

    query = HaulageFreightRateRuleSet.select(HaulageFreightRateRuleSet.base_rate)

    final_data = getattr(rate_calculator, "get_{}_rates".format(location_category))(
        query, commodity, load_type, container_count, ports_distance, wagon_type
    )
    response["success"] = True
    response["list"] = final_data
    return response


def get_india_rates(query, commodity, load_type, container_count, ports_distance, wagon_type):
    final_data = {}
    final_data["distance"] = ports_distance
    if not container_count:
        container_count = 50
        load_type = "Train Load"
    if container_count > 50:
        full_rake_count = container_count / 50
        remaining_wagons_count = container_count % 50
        rake_price = query = query.where(
            HaulageFreightRateRuleSet.distance <= ports_distance,
            HaulageFreightRateRuleSet.distance >= ports_distance - 50,
            HaulageFreightRateRuleSet.commodity_class_type == commodity,
            HaulageFreightRateRuleSet.train_load_type == "Train Load",
        )
        wagon_price = query = query.where(
            HaulageFreightRateRuleSet.distance <= ports_distance,
            HaulageFreightRateRuleSet.distance >= ports_distance - 50,
            HaulageFreightRateRuleSet.commodity_class_type == commodity,
            HaulageFreightRateRuleSet.train_load_type == "Wagon Load",
        )
        rake_price_per_tonne = rake_price.dicts().get()
        wagon_price_per_tonne = wagon_price.dicts().get()
        final_rake_price = rake_price_per_tonne * full_rake_count * 50 * DEFAULT_PERMISSIBLE_CARRYING_CAPACITY
        final_wagon_price = wagon_price_per_tonne * remaining_wagons_count * DEFAULT_PERMISSIBLE_CARRYING_CAPACITY
        final_data["base_price"] = final_rake_price + final_wagon_price

    else:
        query = query.where(
            HaulageFreightRateRuleSet.distance <= ports_distance,
            HaulageFreightRateRuleSet.distance >= ports_distance - 50,
            HaulageFreightRateRuleSet.commodity_class_type == commodity,
            HaulageFreightRateRuleSet.train_load_type == load_type,
        )
        price_per_tonne = query.dicts().get()['base_rate']
        if wagon_type:
            permissible_carrying_capacity = WagonTypes.select(WagonTypes.permissible_carrying_capacity).where(WagonTypes.wagon_code == wagon_type)
            price = float(price_per_tonne) * container_count * int(permissible_carrying_capacity.dicts().get()['permissible_carrying_capacity'])
        else:
            price = float(price_per_tonne) * container_count * DEFAULT_PERMISSIBLE_CARRYING_CAPACITY

        surcharge = 0.15*price
        development_charges = 0.05*price
        other_charges = development_charges + DESTINATION_TERMINAL_CHARGES_INDIA
        final_data["base_price"] = price + surcharge + other_charges
        final_data['currency'] = 'INR'
    return final_data


def get_china_rates(query, commodity, load_type, container_count, ports_distance):
    final_data = {}
    final_data["distance"] = ports_distance
    return
