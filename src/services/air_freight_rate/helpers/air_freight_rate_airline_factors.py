from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.air_freight_rate.models.air_freight_location_cluster_factor import AirFreightLocationClusterFactor
from services.air_freight_rate.models.air_freight_rate_airline_factors import AirFreightAirlineFactors
from peewee import SQL
from database.rails_db import get_past_air_invoices
from fastapi.encoders import jsonable_encoder
from configs.global_constants import DEFAULT_WEIGHT_SLABS
from micro_services.client import common

def create_air_freight_rate_airline_factors():
    cluster_data = AirFreightLocationClusters.select()
    data_list = [(row.id, str(row.base_airport_id)) for row in cluster_data]
    location_data = AirFreightLocationClusterMapping.select(
        AirFreightLocationClusterMapping.location_id,
        AirFreightLocationClusterMapping.cluster_id,
    )
    location_data = jsonable_encoder(list(location_data.dicts()))
    cluster_wise_locs = {}
    for loc in location_data:
        if loc["cluster_id"] in cluster_wise_locs:
            values = cluster_wise_locs[loc["cluster_id"]] or []
            values.append(loc["location_id"])
            cluster_wise_locs[loc["cluster_id"]] = values
        else:
            cluster_wise_locs[loc["cluster_id"]] = [loc["location_id"]]
    for origin_cluster in data_list:
        for destination_cluster in data_list:
            if (
                origin_cluster[1] == "aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19"
                and destination_cluster[1] == "c298f645-7d0a-44cb-845f-da7d85ac0e16"
            ):
            # if origin_cluster != destination_cluster:
                origin_locations = [origin_cluster[1]]
                destination_locations = [destination_cluster[1]]
                air_freight_rates = AirFreightRate.select(
                    AirFreightRate.origin_airport_id,
                    AirFreightRate.destination_airport_id,
                    AirFreightRate.airline_id,
                    AirFreightRate.weight_slabs,
                ).where(
                    AirFreightRate.origin_airport_id << origin_locations,
                    AirFreightRate.destination_airport_id << destination_locations,
                    AirFreightRate.updated_at
                    >= SQL(
                        "date_trunc('MONTH', CURRENT_DATE - INTERVAL '1 months')::DATE"
                    ),
                )
                air_freight_rates = jsonable_encoder(list(air_freight_rates.dicts()))
                invoice_rates = get_past_air_invoices(
                    origin_location_id=origin_locations,
                    destination_location_id=destination_locations,
                    location_type="airport",
                    interval=1,
                )
                if invoice_rates or air_freight_rates:
                    dict = create_airline_dictionary(invoice_rates, air_freight_rates)
                    get_ratios(dict, origin_cluster[0], destination_cluster[0])


def get_bas_price_currency(invoice_rate):
    for line_item in invoice_rate["line_items"]:
        if line_item["code"] == "BAS" and line_item["name"] == "Basic Air Freight":
            return line_item["price"], line_item['currency']
        return None, None


def get_weight_slab_for_invoice_rates(invoice_rate):

    for weight_slab in DEFAULT_WEIGHT_SLABS:
        if (invoice_rate["weight"] >= weight_slab["lower_limit"]and weight_slab["upper_limit"] >= invoice_rate["weight"]):
            return "{}-{}".format(int(weight_slab["lower_limit"]), int(weight_slab["upper_limit"]))


def get_lower_and_upper_limit_matching_for_supply_rates(lower_limit, upper_limit):
    lower_limits = {
        0: "0.0-50",
        50.1: "50-100",
        100.1: "100-300",
        300.1: "300-500",
        500.1: "500-1000",
        1000.1: "1000-10000",
    }
    weight_slab = ""
    difference = 1000001
    for key, value in lower_limits.items():
        if abs(key - lower_limit) <= difference:
            weight_slab = value
            difference = abs(key - lower_limit)
        else:
            break
    return weight_slab

def create_airline_dictionary(invoice_rates, air_freight_rates):
    airline_dictionary = {}

    for invoice_rate in invoice_rates:
        price, currency = get_bas_price_currency(invoice_rate)
        slab = get_weight_slab_for_invoice_rates(invoice_rate)

        if price:
            if not currency=="INR":
                price = common.get_money_exchange_for_fcl({'price':price, 'from_currency': currency, 'to_currency': 'INR'})['price']
            airline_id = invoice_rate["airline_id"]
            if airline_id in airline_dictionary.keys():
                airline_dictionary[airline_id][slab] = airline_dictionary[airline_id].get(slab, []) + [price]
            else:
                airline_dictionary[airline_id] = {slab: [price]}

    for air_freight_rate in air_freight_rates:
        weight_slabs=air_freight_rate['weight_slabs']
        for weight_slab in weight_slabs:
            slab=get_lower_and_upper_limit_matching_for_supply_rates(weight_slab['lower_limit'],weight_slab['upper_limit'])
            price=weight_slab['tariff_price']
            if price:
                if not weight_slab['currency']=="INR":
                    price = common.get_money_exchange_for_fcl({'price':price, 'from_currency': weight_slab['currency'], 'to_currency': 'INR'})['price']
                airline_id = air_freight_rate["airline_id"]
                if airline_id in airline_dictionary.keys():
                    airline_dictionary[airline_id][slab] = airline_dictionary[airline_id].get(slab, []) + [price]
                else:
                    airline_dictionary[airline_id] = {slab: [price]}
    return airline_dictionary


def get_ratios(airline_dictionary, orgin, destination):

    prime_airline_id = max(airline_dictionary,key=lambda airline_id: sum(len(values) for values in airline_dictionary[airline_id].values()))
    max_slab = max(airline_dictionary[prime_airline_id],key=lambda slab: len(airline_dictionary[prime_airline_id][slab]))

    prime_airline_values = airline_dictionary[prime_airline_id][max_slab]
    prime_average = sum(prime_airline_values) / len(prime_airline_values)
    for airline_id, slab_values in airline_dictionary.items():
        if airline_id != prime_airline_id:
            values = slab_values.get(max_slab, [])
            if values:
                average = sum(values) / len(values)
                ratio = prime_average / average
        AirFreightAirlineFactors.create(
                    base_airline_id=prime_airline_id,
                    derive_airline_id=airline_id,
                    origin_cluster_id=orgin,
                    destination_cluster_id=destination,
                    rate_factor=ratio
                )