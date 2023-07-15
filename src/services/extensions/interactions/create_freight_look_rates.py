from datetime import datetime, timedelta
from micro_services.client import common, maps
from configs.global_constants import  DEFAULT_SERVICE_PROVIDER_ID, DEFAULT_PROCURED_BY_ID
from services.extensions.constants.general import commodity_mappings, commodity_type_mappings
from services.air_freight_rate.interactions.create_draft_air_freight_rate import create_draft_air_freight_rate
from services.air_freight_rate.constants.air_freight_rate_constants import DEFAULT_AIRLINE_ID

airline_hash = {}

def create_weight_slabs(rate):
    currency = rate['Crny'] or 'INR'
    rate['NORMAL'] = float(rate.get('NORMAL').strip() or 0) or ''
    rate['+45'] = float((rate.get('+45') or '').strip() or 0) or ''
    rate['+100'] = float((rate.get('+100') or '').strip() or 0) or ''
    rate['+250'] = float((rate.get('+250') or '').strip() or 0) or ''
    rate['+300'] = float((rate.get('+300') or '').strip() or 0) or ''
    rate['+500'] = float((rate.get('+500') or '').strip() or 0) or ''

    price_0_45 = rate['NORMAL'] or rate['+45'] or rate['+100'] or rate['+250']
    price_45_100 = rate['+45'] or rate['+100'] or rate['+250'] or rate['+300']
    price_100_250 = rate['+100'] or rate['+250'] or rate['+45'] or rate['+300']
    price_250_300 = rate['+250'] or rate['+300'] or rate['+100'] or rate['+45']
    price_300_500 = rate['+300'] or rate['+500'] or rate['+250'] or rate['+100']
    price_500_1000 = rate['+500'] or rate['+300'] or rate['+250'] or rate['+100']
    weight_slabs = [
        {
            'upper_limit': 45,
            'lower_limit': 0,
            'currency': currency,
            'unit': 'per_kg',
            'tariff_price': price_0_45
        },
        {
            'upper_limit': 100,
            'lower_limit': 45.1,
            'currency': currency,
            'unit': 'per_kg',
            'tariff_price': price_45_100
        },
        {
            'upper_limit': 250,
            'lower_limit': 100.1,
            'currency': currency,
            'unit': 'per_kg',
            'tariff_price': price_100_250
        },
        {
            'upper_limit': 300,
            'lower_limit': 250.1,
            'currency': currency,
            'unit': 'per_kg',
            'tariff_price': price_250_300
        },
        {
            'lower_limit': 300.1,
            'upper_limit': 500,
            'currency': currency,
            'unit': 'per_kg',
            'tariff_price': price_300_500
        },
        {
            'lower_limit': 500.1,
            'upper_limit': 5000,
            'currency': currency,
            'unit': 'per_kg',
            'tariff_price': price_500_1000
        }
    ]
    return weight_slabs

def format_air_freight_rate(rate, locations):
    weight_slabs = create_weight_slabs(rate=rate)
    minimum_rate = 0
    if rate['MIN.'].strip():
        minimum_rate = float(rate['MIN.'].strip())
    commodity = commodity_mappings.get((rate['SCR'] or '').strip())
    commodity_type = commodity_type_mappings.get((rate['SCR'] or '').strip())
    if not commodity or not commodity_type:
        return None
    rate_obj = {
        'origin_airport_id': locations[rate['Loc .']]['id'],
        'destination_airport_id': rate['destination_airport_id'],
        'weight_slabs': weight_slabs,
        'min_price': minimum_rate,
        'commodity': commodity,
        'commodity_type': commodity_type,
        'commodity_sub_type': None,
        'operation_type': 'passenger',
        'currency': weight_slabs[0]['currency'],
        'price_type': 'net_net',
        'rate_type': 'general',
        'service_provider_id': DEFAULT_SERVICE_PROVIDER_ID,
        'density_category': 'general',
        'performed_by_id': DEFAULT_PROCURED_BY_ID,
        'procured_by_id': DEFAULT_PROCURED_BY_ID,
        'sourced_by_id': DEFAULT_PROCURED_BY_ID,
        'shipment_type': 'box',
        'stacking_type': 'stackable',
        'validity_start': datetime.now(),
        'validity_end': datetime.now() + timedelta(days=7),
        'source': 'freight_look',
        'meta_data': rate['meta_data'] | { 'origin':locations[rate['Loc .']]['name'] }
    }
    return rate_obj

# def read_json():
#     import json
#     f = open('/Users/ssngurjar/chakravyuh/src/services/extensions/interactions/r.json')
#     data = json.load(f)
#     f.close()
#     return data

def create_proper_json(rates):
    headers = rates[0]
    new_rates_obj = rates[1: len(rates)]
    final_rates = []
    for rate in new_rates_obj:
        obj = {}
        for i, item in enumerate(rate):
            key = headers[i]
            obj[key] = item
        final_rates.append(obj)

    return final_rates

def create_air_freight_rate_api(rate, locations):
    airline = None
    airline_id = DEFAULT_AIRLINE_ID
    airline_name = 'deafult'
    if rate['A. Name'].lower() in airline_hash:
        airline = airline_hash[rate['A. Name'].lower()]
    elif 'A. Name' in rate and rate['A. Name']:
        try:
            airline = maps.list_operators({'filters': {'q': rate['A. Name'], 'operator_type': 'airline' }})['list'][0]
            airline_hash[rate['A. Name'].lower()] = airline
        except Exception as e:
            print(e)
       
    if airline and 'id' in airline:
        airline_id = airline['id']
        airline_name = airline['short_name']

    rate_obj = format_air_freight_rate(rate=rate, locations=locations)
    if not rate_obj:
        return rate
    rate_obj['airline_id'] = airline_id
    rate_obj['meta_data']['airline'] = airline_name
    res = create_draft_air_freight_rate(rate_obj)
    # res = common.create_air_freight_rate(rate_obj)
    return res

def get_locations(destination, all_port_codes: list = []):
    all_locations = maps.list_locations({ 'filters': { 'port_code': all_port_codes, 'country_code': 'IN', 'type': 'airport' }, 'includes': {'port_code': True, 'id': True, 'name': True },'page_limit': 50 })
    all_locations_destination = maps.list_locations({ 'filters': { 'q': destination, 'type': 'airport' }, 'includes': {'port_code': True, 'id': True, 'name': True },'page_limit': 50 })
    all_locations_hash = {}
    if 'list' in all_locations and len(all_locations['list']):
        for location in all_locations['list']:
            all_locations_hash[location['port_code']] = location
    
    if 'list' in all_locations_destination and len(all_locations_destination['list']):
        for location in all_locations_destination['list']:
            all_locations_hash[location['port_code']] = location
    
    return all_locations_hash



def create_freight_look_rates(request):
    from celery_worker import process_freight_look_rates
    rates = request['rates']
    destination = request.get('destination')
    new_rates = rates
    proper_json_rates = create_proper_json(new_rates)
    all_port_codes_hash = {}

    destination_port_code = None
    if destination:
        destination_port_code = destination.split('-')[0].strip()
        if destination_port_code:
            all_port_codes_hash[destination_port_code] = True

    for rate in proper_json_rates:
        all_port_codes_hash[rate['Loc .']] = True
    
    all_port_codes = list(all_port_codes_hash.keys())


    locations = get_locations(destination, all_port_codes=all_port_codes)

    for rate in proper_json_rates:
        rate['destination_airport_id'] = locations[destination_port_code]['id']
        rate['meta_data'] = {}
        rate['meta_data']['destination'] = locations[destination_port_code]['name']
        try:
            process_freight_look_rates.apply_async(kwargs = { 'rate': rate, 'locations': locations }, queue='low')
            # new_rate = create_air_freight_rate_api(rate=rate, locations=locations)
        except Exception as e:
            print(e)
        

    return True