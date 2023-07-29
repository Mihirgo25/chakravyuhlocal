from services.chakravyuh.setters.air_freight import AirFreightVyuh as AirFreightVyuhSetters
from database.rails_db import get_invoices
from services.air_freight_rate.models.air_freight_location_cluster import AirFreightLocationCluster
from fastapi.encoders import jsonable_encoder
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from database.rails_db import get_past_air_invoices
from peewee import SQL

def invoice_rates_updation():
    freight_rates = get_invoices()
    for freight_rate in freight_rates:
        line_items = freight_rate['line_items']
        actual_lineitem = None
        bas_count = 0
        for line_item in line_items:
            if line_item['code'] == 'BAS' and line_item['unit'] == 'per_kg':
                actual_lineitem = line_item
                bas_count = bas_count + 1
            if line_item['code'] == 'BAS' and line_item['unit'] == 'per_shipment' and not actual_lineitem:
                actual_lineitem = line_item
                bas_count = bas_count + 1
                actual_lineitem['price'] = (line_item['price'] / (freight_rate['chargeable_weight'] or freight_rate['weight']))
        if actual_lineitem and bas_count == 1:
            freight_rate['price'] = actual_lineitem['price']
            freight_rate['unit'] = actual_lineitem['unit']
            freight_rate['currency'] = actual_lineitem['currency']
        if bas_count ==1:
            freight_rate['shipment_type'] = 'box'
            if freight_rate['packages']:
                package = freight_rate['packages'][0]
                freight_rate['shipment_type'] = package['packing_type']
            setter = AirFreightVyuhSetters(freight_rate)
            setter.set_dynamic_pricing()
    return True


def critical_rates():
    cluster_data = AirFreightLocationCluster.select(
        AirFreightLocationCluster.id, AirFreightLocationCluster.base_airport_id
    )
    data_list = jsonable_encoder(list(cluster_data.dicts()))
    for origin_cluster in data_list:
        for destination_cluster in data_list:
            if origin_cluster != destination_cluster and origin_cluster['id']==3:
                freight_rates =  AirFreightRate.select(
                    AirFreightRate.id,
                    AirFreightRate.airline_id,
                    AirFreightRate.stacking_type,
                    AirFreightRate.shipment_type,
                    AirFreightRate.weight_slabs,
                    AirFreightRate.commodity,
                    AirFreightRate.commodity_type,
                    AirFreightRate.commodity_sub_type,
                    AirFreightRate.operation_type,
                    AirFreightRate.origin_airport_id,
                    AirFreightRate.destination_airport_id
                ).where(
                    AirFreightRate.origin_airport_id == origin_cluster['base_airport_id'],
                    AirFreightRate.destination_airport_id == destination_cluster['base_airport_id'],
                    AirFreightRate.commodity == "general",
                    AirFreightRate.source << ['manual','rate_sheets'],
                    # AirFreightRate.updated_at>= SQL("date_trunc('week', CURRENT_DATE - INTERVAL '1 weeks')::DATE"),
                    )
                freight_rates = jsonable_encoder(list(freight_rates.dicts())) 
                csr_rate = True
                if not freight_rates:
                    csr_rate = False
                    freight_rates = get_past_air_invoices(
                        origin_location_id=[origin_cluster['base_airport_id']],
                        destination_location_id=[destination_cluster['base_airport_id']],
                        location_type="airport",
                        interval=1,
                        interval_type = 'week',
                        interval_types = 'weeks'
                    )
                if not freight_rates:
                    continue
                freight_rate = get_prime_airline_freight_rate(freight_rates)
                if not csr_rate:
                    line_items = freight_rate['line_items']
                    actual_lineitem = None
                    bas_count = 0
                    for line_item in line_items:
                        if line_item['code'] == 'BAS' and line_item['unit'] == 'per_kg':
                            actual_lineitem = line_item
                            bas_count = bas_count + 1
                        if line_item['code'] == 'BAS' and line_item['unit'] == 'per_shipment' and not actual_lineitem:
                            actual_lineitem = line_item
                            bas_count = bas_count + 1
                            actual_lineitem['price'] = (line_item['price'] / (freight_rate['chargeable_weight'] or freight_rate['weight']))
                    if actual_lineitem and bas_count == 1:
                        freight_rate['price'] = actual_lineitem['price']
                        freight_rate['unit'] = actual_lineitem['unit']
                        freight_rate['currency'] = actual_lineitem['currency']
                    if bas_count ==1:
                        freight_rate['shipment_type'] = 'box'
                        if freight_rate['packages']:
                            package = freight_rate['packages'][0]
                            freight_rate['shipment_type'] = package['packing_type']
                    else:
                        continue
                
                setter = AirFreightVyuhSetters(new_rate=freight_rate,csr=csr_rate)
                setter.insert_rates_to_rms()


def get_prime_airline_freight_rate(freight_rates):
    airline_wise_count_dict = {}
    for freight in freight_rates:
        if not freight['airline_id'] in airline_wise_count_dict:
            airline_wise_count_dict[freight['airline_id']]=0
        airline_wise_count_dict[freight['airline_id']]+=1
    sorted(freight_rates,key=lambda x: airline_wise_count_dict[x['airline_id']],reverse=True)
    return freight_rates[0]

    