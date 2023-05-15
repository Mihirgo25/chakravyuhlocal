from services.haulage_freight_rate.models.haulage_freight_rate_rule_sets import HaulageFreightRateRuleSet
import geopy.distance
from micro_services.client import maps
import services.haulage_freight_rate.interactions.rate_calculator as rate_calculator
from configs.rails_constants import DEFAULT_PERMISSIBLE_CARRYING_CAPACITY

POSSIBLE_LOCATION_CATEGORY = ["india", "china", "europe", "north_america"]


def get_distance(origin_location, destination_location):
    input = {"filters": {"id": [origin_location, destination_location]}}
    data = maps.list_locations(input)
    if data:
        data = data["list"]
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
):
    response = {"success": False, "status_code": 200}

    location_category =''

    #check valid location
    if location_category not in POSSIBLE_LOCATION_CATEGORY:
        return response

    #check intermodal


    ports_distance = get_distance(origin_location, destination_location)

    if not container_count:
        load_type = "Wagon Load"

    query = HaulageFreightRateRuleSet.select(HaulageFreightRateRuleSet.base_rate)

    final_data = getattr(rate_calculator, "get_{}_rates".format(location_category))(
        query, commodity, load_type, container_count, ports_distance
    )

    response["success"] = True
    response["list"] = final_data
    return response


def get_india_rates(query, commodity, load_type, container_count, ports_distance):
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
            HaulageFreightRateRuleSet.commodity_type == commodity,
            HaulageFreightRateRuleSet.load_type == "Train Load",
        )
        wagon_price = query = query.where(
            HaulageFreightRateRuleSet.distance <= ports_distance,
            HaulageFreightRateRuleSet.distance >= ports_distance - 50,
            HaulageFreightRateRuleSet.commodity_type == commodity,
            HaulageFreightRateRuleSet.load_type == "Wagon Load",
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
            HaulageFreightRateRuleSet.commodity_type == commodity,
            HaulageFreightRateRuleSet.load_type == load_type,
        )

        price_per_tonne = query.dicts().get()
        price = price_per_tonne * container_count * DEFAULT_PERMISSIBLE_CARRYING_CAPACITY
        final_data["base_price"] = price
    return final_data


def get_china_rates(query, commodity, load_type, container_count, ports_distance):
    final_data = {}
    final_data["distance"] = ports_distance
    return
