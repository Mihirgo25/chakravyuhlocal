from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_location_cluster import AirFreightLocationCluster
from services.air_freight_rate.models.air_freight_airline_factor import AirFreightAirlineFactor
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_past_air_invoices,get_spot_search_count
from services.air_freight_rate.constants.air_freight_rate_constants import DEFAULT_FACTORS_WEIGHT_SLABS
from micro_services.client import common,maps
from peewee import SQL
from statistics import mean 
from services.air_freight_rate.helpers.get_matching_weight_slab import get_matching_slab

class RelateAirline:
    def __init__(self):
        self.default_factor = 1
        
    def get_available_rates(self, origin_locations, destination_locations):
        air_freight_rates = AirFreightRate.select(
            AirFreightRate.origin_airport_id,
            AirFreightRate.destination_airport_id,
            AirFreightRate.airline_id,
            AirFreightRate.weight_slabs,
            AirFreightRate.id
        ).where(
            AirFreightRate.origin_airport_id << origin_locations,
            AirFreightRate.destination_airport_id << destination_locations,
            AirFreightRate.commodity == "general",
            AirFreightRate.updated_at
            >= SQL("date_trunc('week', CURRENT_DATE - INTERVAL '1 weeks')::DATE"),
            AirFreightRate.source << ['manual','rate_sheets',''],
            ~(AirFreightRate.rate_not_available_entry)
        )
        air_freight_rates = jsonable_encoder(list(air_freight_rates.dicts()))
        return air_freight_rates

    def get_bas_price_currency(self, invoice_rate):
        for line_item in invoice_rate["line_items"]:
            if line_item["code"] == "BAS" and line_item["name"] == "Basic Air Freight" and line_item['unit']=='per_kg':
                return line_item["price"], line_item["currency"]
            return None, None

    def get_weight_slab_for_invoice_rates(self, invoice_rate):
        for weight_slab in DEFAULT_FACTORS_WEIGHT_SLABS:
            if (invoice_rate["weight"] >= weight_slab["lower_limit"]and weight_slab["upper_limit"] >= invoice_rate["weight"]):
                return "{}-{}".format(int(weight_slab["lower_limit"]), int(weight_slab["upper_limit"]))


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
                
        crirtical_airline_dict = {}
        critical_rate = None
        id = None
        for air_freight_rate in air_freight_rates:
            weight_slabs = air_freight_rate["weight_slabs"]
            for weight_slab in weight_slabs:
                price = weight_slab["tariff_price"]
                if not weight_slab["currency"] == "INR":
                    price = common.get_money_exchange_for_fcl(
                        {
                            "price": price,
                            "from_currency": weight_slab["currency"],
                            "to_currency": "INR",
                        }
                    )["price"]
                weight_slab['tariff_price'] = price

            if not air_freight_rate['airline_id'] in crirtical_airline_dict:
                crirtical_airline_dict[air_freight_rate['airline_id']] = 0
            crirtical_airline_dict[air_freight_rate['airline_id']] +=1
            if prime_airline_id_count < crirtical_airline_dict[air_freight_rate['airline_id']]:
                    prime_airline_id = air_freight_rate['airline_id']
                    prime_airline_id_count = crirtical_airline_dict[air_freight_rate['airline_id']]
                    critical_rate = weight_slabs
                    id = air_freight_rate['id']
                                                
        return prime_airline_id, airline_dictionary,critical_rate

    def relate_airlines(self):
        cluster_data = AirFreightLocationCluster.select(
            AirFreightLocationCluster.id, AirFreightLocationCluster.base_airport_id
        )
        location_mappings = AirFreightLocationClusterMapping.select(AirFreightLocationClusterMapping.cluster_id,AirFreightLocationClusterMapping.location_id)
        location_mappings = jsonable_encoder(list(location_mappings.dicts()))
        location_mappings_dict = {}
        for location in location_mappings:
            if location['cluster_id'] in location_mappings_dict.keys():
                location_mappings_dict[location['cluster_id']] = location_mappings_dict[location['cluster_id']] + [location['location_id']]
            else:
                location_mappings_dict[location['cluster_id']] = [location['location_id']]
        data_list = jsonable_encoder(list(cluster_data.dicts()))
        for origin_cluster in data_list:
            for destination_cluster in data_list:
                if origin_cluster != destination_cluster:
                    origin_locations = [origin_cluster['base_airport_id']] 
                    destination_locations = [destination_cluster['base_airport_id']] 
                    air_freight_rates = self.get_available_rates(origin_locations, destination_locations)
                    if not air_freight_rates:
                        continue
                    origin_locations.extend(location_mappings_dict[origin_cluster['id']])
                    destination_locations.extend(location_mappings_dict[destination_cluster['id']])
                    invoice_rates = get_past_air_invoices(
                        origin_location_id=origin_locations,
                        destination_location_id=destination_locations,
                        location_type="airport",
                        interval=1,
                        interval_type = 'month',
                        interval_types = 'months'
                    )
                    if not invoice_rates or not air_freight_rates:
                        continue
                    prime_airline_id, airline_dict, critical_rate= self.create_airline_dictionary(invoice_rates, air_freight_rates,origin_cluster['base_airport_id'],destination_cluster['base_airport_id'])
                    self.generate_ratios(prime_airline_id,airline_dict,origin_cluster,destination_cluster,origin_locations,destination_locations,critical_rate)


    def get_airlines_for_airport_pair(self,origin_airport_id,destination_airport_id):
        data = {
            'origin_airport_id': origin_airport_id,
            'destination_airport_id': destination_airport_id
        }
        airlines = maps.get_airlines_for_route(data)

        return airlines

    def generate_ratios(self,prime_arline_id,airline_dict,origin_cluster,destination_cluster,origin_locations,destination_locations,critical_rate):
        origin_base_airport_id = origin_cluster['base_airport_id']
        destination_base_airport_id = destination_cluster['base_airport_id']
        key = ":".join([origin_base_airport_id,destination_base_airport_id,prime_arline_id])
        origin_locations.append(origin_base_airport_id)
        destination_locations.append(destination_base_airport_id)
        for origin in origin_locations:
            for destination in destination_locations:
                if origin!=origin_base_airport_id and destination!=destination_base_airport_id:
                    spot_search_count = get_spot_search_count(origin,destination)
                    if spot_search_count < 10:
                        continue
                    airlines = self.get_airlines_for_airport_pair(origin,destination)['airline_ids']
                    for airline in airlines:
                        key = ":".join([origin,destination,airline])
                        slab_wise_ratio = {}
                        if key in airline_dict:
                            slab_wise_ratio = self.get_ratio(critical_rate,airline_dict[key])
                        self.airline_factors_insertion(slab_wise_ratio,origin,destination,prime_arline_id,airline,origin_cluster['id'],destination_cluster['id'])
                        

    def airline_factors_insertion(self,slab_wise_ratio,origin,destination,prime_airline_id,airline,origin_cluster_id,destination_cluster_id):
        slabs = {
            "0.0-45":1,
            "45-100":1,
            "100-300":1,
            "300-500":1,
            "500-5000":1,
        }
        for key,value in slab_wise_ratio.items():
            slabs[key] = value
        
        airline_factor = AirFreightAirlineFactor.select().where(
            AirFreightAirlineFactor.origin_airport_id == origin,
            AirFreightAirlineFactor.destination_airport_id == destination,
            AirFreightAirlineFactor.derive_airline_id == airline
        ).first()
        if not airline_factor:
            airline_factor = AirFreightAirlineFactor(**{'origin_airport_id':origin,'destination_airport_id':destination,'origin_cluster_id':origin_cluster_id,'destination_cluster_id':destination_cluster_id})

        airline_factor.derive_airline_id = airline
        airline_factor.base_airline_id = prime_airline_id
        airline_factor.slab_wise_factor = slabs
        try:
            airline_factor.save()
        except Exception as e:
            pass

    def get_ratio(self,criticl_weight_slabs,weight_slabs):
        slab_wise_ratio = {}
        for slab in criticl_weight_slabs:
            key = get_matching_slab(slab["lower_limit"])
            if key in weight_slabs:
                slab_wise_ratio[key] = mean(weight_slabs[key]/slab['tariff_price'])
        
        return slab_wise_ratio
    


                
