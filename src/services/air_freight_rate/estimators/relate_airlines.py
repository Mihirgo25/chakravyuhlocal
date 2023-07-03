from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
from services.air_freight_rate.models.air_freight_rate_airline_factors import AirFreightAirlineFactors
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_past_air_invoices
from configs.global_constants import DEFAULT_WEIGHT_SLABS
from micro_services.client import common
from peewee import SQL
import uuid


class RelateAirline:
    def __init__(self):
        self.default_factor = 1
        
    def get_available_rates(self, origin_locations, destination_locations):
        air_freight_rates = AirFreightRate.select(
            AirFreightRate.origin_airport_id,
            AirFreightRate.destination_airport_id,
            AirFreightRate.airline_id,
            AirFreightRate.weight_slabs,
        ).where(
            AirFreightRate.origin_airport_id == origin_locations,
            AirFreightRate.destination_airport_id == destination_locations,
            AirFreightRate.commodity == "general",
            AirFreightRate.updated_at
            >= SQL("date_trunc('MONTH', CURRENT_DATE - INTERVAL '1 months')::DATE"),
        )
        air_freight_rates = jsonable_encoder(list(air_freight_rates.dicts()))
        return air_freight_rates

    def get_bas_price_currency(self, invoice_rate):
        for line_item in invoice_rate["line_items"]:
            if line_item["code"] == "BAS" and line_item["name"] == "Basic Air Freight":
                return line_item["price"], line_item["currency"]
            return None, None

    def get_weight_slab_for_invoice_rates(self, invoice_rate):
        for weight_slab in DEFAULT_WEIGHT_SLABS:
            if (invoice_rate["weight"] >= weight_slab["lower_limit"]and weight_slab["upper_limit"] >= invoice_rate["weight"]):
                return "{}-{}".format(int(weight_slab["lower_limit"]), int(weight_slab["upper_limit"]))

    def get_matching_slab(self, lower_limit, upper_limit):
        lower_limits = {
            0: "0.0-45",
            45.1: "45-100",
            100.1: "100-300",
            300.1: "300-500",
            500.1: "500-5000",
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

    def create_airline_dictionary(self, invoice_rates, air_freight_rates):
        airline_dictionary = {}

        for invoice_rate in invoice_rates:
            price, currency = self.get_bas_price_currency(invoice_rate)
            slab = self.get_weight_slab_for_invoice_rates(invoice_rate)

            if price:
                if not currency == "INR":
                    price = common.get_money_exchange_for_fcl(
                        {
                            "price": price,
                            "from_currency": currency,
                            "to_currency": "INR",
                        }
                    )["price"]
                airline_id = invoice_rate["airline_id"]
                if airline_id in airline_dictionary.keys():
                    airline_dictionary[airline_id][slab] = airline_dictionary[
                        airline_id
                    ].get(slab, []) + [price]
                else:
                    airline_dictionary[airline_id] = {slab: [price]}

        prime_air_line_id = max(airline_dictionary,key=lambda airline_id: len(airline_dictionary[airline_id]))

        for air_freight_rate in air_freight_rates:
            weight_slabs = air_freight_rate["weight_slabs"]
            for weight_slab in weight_slabs:
                slab = self.get_matching_slab(weight_slab["lower_limit"], weight_slab["upper_limit"])
                price = weight_slab["tariff_price"]
                if price:
                    if not weight_slab["currency"] == "INR":
                        price = common.get_money_exchange_for_fcl(
                            {
                                "price": price,
                                "from_currency": weight_slab["currency"],
                                "to_currency": "INR",
                            }
                        )["price"]
                    airline_id = air_freight_rate["airline_id"]
                    if airline_id in airline_dictionary.keys():
                        airline_dictionary[airline_id][slab] = airline_dictionary[airline_id].get(slab, []) + [price]
                    else:
                        airline_dictionary[airline_id] = {slab: [price]}
        return prime_air_line_id, airline_dictionary

    def get_ratios(self, prime_airline_id, airline_dictionary, orgin, destination):
        max_slab = max(airline_dictionary[prime_airline_id],key=lambda slab: len(airline_dictionary[prime_airline_id][slab]),)

        prime_airline_values = airline_dictionary[prime_airline_id][max_slab]
        prime_average = sum(prime_airline_values) / len(prime_airline_values)
        for airline_id, slab_values in airline_dictionary.items():
            if airline_id != prime_airline_id:
                values = slab_values.get(max_slab, [])
                if values:
                    average = sum(values) / len(values)
                    ratio = average / prime_average
                AirFreightAirlineFactors.create(
                    base_airline_id=prime_airline_id,
                    derive_airline_id=airline_id,
                    origin_cluster_id=orgin,
                    destination_cluster_id=destination,
                    rate_factor=ratio,
                )

    def relate_airlines(self):
        cluster_data = AirFreightLocationClusters.select(
            AirFreightLocationClusters.id, AirFreightLocationClusters.base_airport_id
        )
        data_list = jsonable_encoder(list(cluster_data.dicts()))
        for origin_cluster in data_list:
            for destination_cluster in data_list:
                if origin_cluster != destination_cluster:
                    origin_locations = uuid.UUID(origin_cluster['base_airport_id'])
                    destination_locations = uuid.UUID(destination_cluster['base_airport_id'])
                    air_freight_rates = self.get_available_rates(origin_locations, destination_locations)
                    invoice_rates = get_past_air_invoices(
                        origin_location_id=origin_locations,
                        destination_location_id=destination_locations,
                        location_type="airport",
                        interval=2,
                    )
                    if invoice_rates or air_freight_rates:
                        prime_airline_id, dict = self.create_airline_dictionary(invoice_rates, air_freight_rates)
                        self.get_ratios(prime_airline_id,dict,origin_cluster[0],destination_cluster[0])
