
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.air_freight_rate.models.air_freight_location_cluster_factor import AirFreightLocationClusterFactor
from services.air_freight_rate.models.air_freight_rate_airline_factors import AirFreightAirlineFactors
from peewee import SQL
from database.rails_db import get_past_air_invoices
from fastapi.encoders import jsonable_encoder

def create_air_freight_rate_airline_factors():
    print("hello")
    cluster_data = AirFreightLocationClusters.select()
    data_list = [(row.id,str(row.base_airport_id)) for row in cluster_data]
    location_data=AirFreightLocationClusterMapping.select(AirFreightLocationClusterMapping.location_id,AirFreightLocationClusterMapping.cluster_id)
    location_data = jsonable_encoder(list(location_data.dicts()))
    cluster_wise_locs = {}
    for loc in location_data:
        if loc['cluster_id'] in cluster_wise_locs:
            values = cluster_wise_locs[loc['cluster_id']] or []
            values.append(loc['location_id'])
            cluster_wise_locs[loc['cluster_id']] = values
        else:
            cluster_wise_locs[loc['cluster_id']] = [loc['location_id']]
    for origin_cluster in data_list:
        for destination_cluster in data_list:
            if origin_cluster[1]=='aa0e7e59-cbb9-43b2-98ce-1f992ae7ab19' and destination_cluster[1]=='c298f645-7d0a-44cb-845f-da7d85ac0e16':


                origin_locations = [origin_cluster[1]]
                destination_locations = cluster_wise_locs[destination_cluster[0]]+[destination_cluster[1]]
                air_freight_rates = AirFreightRate.select(AirFreightRate.origin_airport_id,AirFreightRate.destination_airport_id,AirFreightRate.airline_id,AirFreightRate.weight_slabs).where(
                    AirFreightRate.origin_airport_id << origin_locations,
                    AirFreightRate.destination_airport_id << destination_locations,
                    AirFreightRate.updated_at >= SQL("date_trunc('MONTH', CURRENT_DATE - INTERVAL '1 months')::DATE")
                )
                air_freight_rates = jsonable_encoder(list(air_freight_rates.dicts()))
                invoice_rates = get_past_air_invoices(origin_location_id =origin_locations,destination_location_id =destination_locations ,location_type='airport',interval=1)
                dict=create_airline_dictionary(invoice_rates,air_freight_rates)
                get_ratios(dict,origin_cluster[0],destination_cluster[0])

def get_supply_rates(air_freight_rates,weight,airline_id):
    for air_freight_rate in air_freight_rates:
        if air_freight_rate['airline_id']==airline_id :
                    return air_freight_rate['weight_slab']['tariff_price']

def get_bas_price(invoice_rate):
        for line_item in invoice_rate['line_items']:
            if line_item['code'] == 'BAS' and line_item['name']=='Basic Air Freight':
                return line_item['price']
               

def create_airline_dictionary(invoice_rates,air_freight_rates):
    airline_dictionary={}
    for invoice_rate in invoice_rates:
        price=get_bas_price(invoice_rate)
        if price:
            if invoice_rate['airline_id'] in airline_dictionary.keys():
                airline_dictionary[invoice_rate['airline_id']].append(price)
            else:
                airline_dictionary[invoice_rate['airline_id']]=[price]
    return airline_dictionary

def get_ratios(airline_dictionary,orgin,destination):
    prime_airline_id = max(airline_dictionary, key=lambda key: len(airline_dictionary[key]))

    prime_airline_avergae_price=sum(airline_dictionary[prime_airline_id])/len(airline_dictionary[prime_airline_id])
    for key , value in airline_dictionary.items():
         if key!=prime_airline_id:
              avg=sum(value)/len(value)
              ratio = prime_airline_avergae_price/avg
              print(ratio)
              AirFreightAirlineFactors.create(
                   base_airline_id=prime_airline_id,
                   derive_airline_id=key,
                   origin_cluster_id=orgin,
                   destination_cluster_id=destination,
                   rate_factor=ratio
              )