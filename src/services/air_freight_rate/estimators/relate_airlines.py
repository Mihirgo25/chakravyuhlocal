from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
from services.air_freight_rate.models.air_freight_rate_airline_factors import AirFreightAirlineFactors
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_past_air_invoices
from configs.global_constants import DEFAULT_WEIGHT_SLABS
from micro_services.client import common,maps
from peewee import SQL
from services.air_freight_rate.constants.air_freight_rate_constants import DEFAULT_SERVICE_PROVIDER_ID,DEFAULT_FACTOR
from configs.env import DEFAULT_USER_ID
from datetime import datetime,timedelta
from celery_worker import create_air_freight_rate_delay

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
            AirFreightRate.origin_airport_id << origin_locations,
            AirFreightRate.destination_airport_id << destination_locations,
            AirFreightRate.commodity == "general",
            AirFreightRate.updated_at
            >= SQL("date_trunc('MONTH', CURRENT_DATE - INTERVAL '1 months')::DATE"),
            AirFreightRate.mode << ['manual','rate_sheets']
        )
        air_freight_rates = jsonable_encoder(list(air_freight_rates.dicts()))
        return air_freight_rates

    def get_bas_price_currency(self, invoice_rate):
        for line_item in invoice_rate["line_items"]:
            if line_item["code"] == "BAS" and line_item["name"] == "Basic Air Freight" and line_item['unit']=='per_kg':
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

    def create_airline_dictionary(self, invoice_rates, air_freight_rates,origin_base_airport_id,destination_base_airport_id):
        airline_dictionary = {}
        prime_airline_id = ""
        prime_airline_id_count =0 
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
                key  = ":".join([invoice_rate['origin_airport_id'],invoice_rate['destination_airport_id'],invoice_rate['airline_id']])
                if key in airline_dictionary.keys():
                    airline_dictionary[key][slab] = airline_dictionary[
                        key
                    ].get(slab, []) + [price]
                else:
                    airline_dictionary[key] = {slab: [price]}
                
                if origin_base_airport_id == invoice_rate['origin_airport_id'] and destination_base_airport_id == invoice_rate['destination_airport_id']:
                    if prime_airline_id_count > airline_dictionary[key]:
                        prime_airline_id = invoice_rate['airline_id']


        for air_freight_rate in air_freight_rates:
            weight_slabs = air_freight_rate["weight_slabs"]
            for weight_slab in weight_slabs:
                slab = self.get_matching_slab(weight_slab["lower_limit"], weight_slab["upper_limit"])
                price = weight_slab["tariff_price"]
                if price and price <1000:
                    if not weight_slab["currency"] == "INR":
                        price = common.get_money_exchange_for_fcl(
                            {
                                "price": price,
                                "from_currency": weight_slab["currency"],
                                "to_currency": "INR",
                            }
                        )["price"]
                    key  = ":".join([air_freight_rate['origin_airport_id'],air_freight_rate['destination_airport_id'],air_freight_rate['airline_id']])
                    if key in airline_dictionary.keys():
                        airline_dictionary[key][slab] = airline_dictionary[key].get(slab, []) + [price]
                    else:
                        airline_dictionary[key] = {slab: [price]}
        return prime_airline_id, airline_dictionary

    def get_ratios(self, prime_airline_id, airline_dictionary, origin, destination):
        max_slab = max(airline_dictionary[prime_airline_id],key=lambda slab: len(airline_dictionary[prime_airline_id][slab]),)

        prime_airline_values = airline_dictionary[prime_airline_id][max_slab]
        prime_average = sum(prime_airline_values) / len(prime_airline_values)

        for airline_id, slab_values in airline_dictionary.items():
            if airline_id != prime_airline_id:
                values = slab_values.get(max_slab, [])
                if values:
                    average = sum(values) / len(values)
                    ratio = average / prime_average



    def relate_airlines(self):
        cluster_data = AirFreightLocationClusters.select(
            AirFreightLocationClusters.id, AirFreightLocationClusters.base_airport_id
        )
        location_mappings = AirFreightLocationClusterMapping.select(AirFreightLocationClusterMapping.cluster_id,AirFreightLocationClusterMapping.location_id)
        location_mappings = jsonable_encoder(list(location_mappings.dicts()))
        location_mappings_dict = {}
        for location in location_mappings:
            if location['cluster_id'] in location_mappings.keys():
                location_mappings_dict[location['cluster_id']] = location_mappings_dict[location['cluster_id']] + location['location_id']
            else:
                location_mappings_dict[location['cluster_id']] = location['location_id']
       
        data_list = jsonable_encoder(list(cluster_data.dicts()))
        for origin_cluster in data_list:
            for destination_cluster in data_list:
                if origin_cluster != destination_cluster:
                    origin_locations = [origin_cluster['base_airport_id']] 
                    destination_locations = [destination_cluster['base_airport_id']] 
                    air_freight_rates = self.get_available_rates(origin_locations, destination_locations)
                    invoice_rates = get_past_air_invoices(
                        origin_location_id=origin_locations,
                        destination_location_id=destination_locations,
                        location_type="airport",
                        interval=1,
                        interval_type = 'week',
                        interval_types = 'weeks'
                    )
                    if invoice_rates or air_freight_rates:
                        prime_airline_id, airline_dict = self.create_airline_dictionary(invoice_rates, air_freight_rates,origin_cluster['base_airport_id'],destination_cluster['base_airport_id'])
                        origin_locations = [location_mappings_dict[origin_cluster['cluster_id']]]
                        destination_locations = [location_mappings_dict[destination_cluster['cluster_id']]]
                        self.get_ratios(prime_airline_id,airline_dict,origin_cluster['base_airport_id'],destination_cluster['base_airport_id'],origin_locations,destination_locations)


    def get_airlines_for_airport_pair(self,origin_airport_id,destination_airport_id):
        data = {
            'origin_airport_id': origin_airport_id,
            'destination_airport_id': destination_airport_id
        }
        airlines = maps.get_airlines_for_route(data)

        return airlines

    def generate_ratios(self,prime_arline_id,airline_dict,origin_base_airport_id,destination_base_airport_id,origin_locations,destination_locations):
        base_airport_pair_weight_slab = airline_dict[origin_base_airport_id:destination_base_airport_id:prime_arline_id]
        origin_locations.append(origin_base_airport_id)
        destination.append(destination_base_airport_id)
        for origin in origin_locations:
            for destination in destination_locations:
                airlines = self.get_airlines_for_airport_pair(origin,destination)
                for airline in airlines:
                    key = ":".join([origin,destination,airline])
                    if key in airline_dict:
                        slab_wise_ratio = self.get_ratio(base_airport_pair_weight_slab,airline_dict[key])
                        create_params = self.get_rate_param(origin,destination,base_airport_pair_weight_slab,slab_wise_ratio,airline)
                    else:
                        create_params = self.get_rate_param(origin,destination,base_airport_pair_weight_slab,{},airline)
                    
                    create_air_freight_rate_delay.apply_async(kwargs = {'request':create_params})

    def get_ratio(self,criticl_weight_slabs,weight_slabs):
        slab_wise_ratio = {}
        for key,value in criticl_weight_slabs.items():
            if key in weight_slabs:
                slab_wise_ratio[key] = value/weight_slabs[key]
        
        return slab_wise_ratio
    
    def get_rate_param(self,origin_airport_id,destination_airport_id,weight_slabs,ratio_dict ,airline_id):
        params = {
            'origin_airport_id':origin_airport_id,
            'destination_airport_id':destination_airport_id,
            'commodity':'general',
            'commodity_type': 'all',
            'commodity_sub_type': 'all',
            'weight_slabs':self.get_rms_weight_slabs(weight_slabs=weight_slabs,ratio_dict=ratio_dict),
            'airline_id':airline_id,
            'operation_type':'passenger',
            'stacking_type': 'stackable',
            'shipment_type':'box',
            'currency':'INR',
            'price_type':'net_net',
            'min_price' : weight_slabs[0]['tariff_price'],
            'service_provider_id':DEFAULT_SERVICE_PROVIDER_ID,
            'performed_by_id':DEFAULT_USER_ID,
            'procured_by_id':DEFAULT_USER_ID,
            'sourced_by_id':DEFAULT_USER_ID,
            'validity_start': datetime.now().date(),
            'validity_end': datetime.now().date()+ timedelta(days=7)
        }
        return params
    
    def get_rms_weight_slabs(weight_slabs,ratio_dict):
        prev_weight_slab = 0
        first = False
        if not ratio_dict:
            return weight_slabs

        for key,value in weight_slabs.items():
            if key in ratio_dict:
                weight_slabs['tariff_price'] = weight_slabs['tariff_price']/ratio_dict[key]
            elif not first:
                weight_slabs['tariff_price'] =   weight_slabs['tariff_price']
            else:
                weight_slabs['tariff_price'] = prev_weight_slab*DEFAULT_FACTOR
            prev_weight_slab = value['tariff_price']
            if not first:
                first = True
        
        return weight_slabs

                
