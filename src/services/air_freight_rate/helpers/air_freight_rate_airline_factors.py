
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.air_freight_rate.models.air_freight_location_clusters import AirFreightLocationClusters
from services.air_freight_rate.models.air_freight_location_cluster_mapping import AirFreightLocationClusterMapping
from services.air_freight_rate.models.air_freight_location_cluster_factor import AirFreightLocationClusterFactor
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
                air_freight_rates = AirFreightRate.select(AirFreightRate.origin_airport_id,AirFreightRate.destination_airport,AirFreightRate.airline_id,AirFreightRate.weight_slabs).where(
                    AirFreightRate.origin_airport_id << origin_locations,
                    AirFreightRate.destination_airport_id << destination_locations,
                    AirFreightRate.updated_at >= SQL("date_trunc('MONTH', CURRENT_DATE - INTERVAL '1 months')::DATE")
                )
                air_freight_rates = jsonable_encoder(list(air_freight_rates.dicts()))
                invoice_rates = get_past_air_invoices(origin_location_id =origin_locations,destination_location_id =destination_locations ,location_type='airport',interval=1)
                aie=create_airline_dictionary(invoice_rates,air_freight_rates)
                # print(invoice_rates)
                print(aie)
def get_supply_rates(air_freight_rates,weight,airline_id):
    for air_freight_rate in air_freight_rates:
        if air_freight_rate['airline_id']==airline_id :
            for weight_slab in air_freight_rates['weight_slabs']:
                if weight_slab['lower_limit']>=weight and weight_slab['upper_limit']<=weight:
                    return weight_slab['tariff_price']

def create_airline_dictionary(invoice_rates,air_freight_rates):
    airline_dictionary={}
    for invoice_rate in invoice_rates:
        price=get_supply_rates(air_freight_rates,invoice_rate['weight'],invoice_rate['airline_id'])
        if invoice_rate['airline_id'] in airline_dictionary.keys():
            airline_dictionary[invoice_rate['airline_id']].append(invoice_rate['price'])
        else:
            airline_dictionary[invoice_rate['airline_id']]=[invoice_rate['price']]
        airline_dictionary[invoice_rate['airline_id']].append(price)
    return airline_dictionary

def get_ratios(airline_dictionary):
    prime_airline_id = max(airline_dictionary, key=lambda key: len(airline_dictionary[key]))
