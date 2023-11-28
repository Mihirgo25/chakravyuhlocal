from datetime import datetime, timedelta
from micro_services.client import common, maps
from configs.global_constants import  DEFAULT_SERVICE_PROVIDER_ID, DEFAULT_PROCURED_BY_ID
from services.extensions.constants.general import commodity_mappings, commodity_type_mappings, airline_ids, airline_margins, surcharge_performed_by_id
from services.air_freight_rate.interactions.create_draft_air_freight_rate import create_draft_air_freight_rate
from services.air_freight_rate.constants.air_freight_rate_constants import DEFAULT_AIRLINE_ID, COGOXPRESS
from services.extensions.helpers.freight_look_helpers import get_locations,create_proper_json
from services.air_freight_rate.interactions.create_air_freight_rate import create_air_freight_rate
airline_hash = {}

def create_weight_slabs(rate,airline_id):
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
            'tariff_price': price_0_45 + (price_0_45*airline_margins[airline_id])
        },
        {
            'upper_limit': 100,
            'lower_limit': 45.1,
            'currency': currency,
            'unit': 'per_kg',
            'tariff_price': price_45_100 + (price_45_100*airline_margins[airline_id])
        },
        {
            'upper_limit': 250,
            'lower_limit': 100.1,
            'currency': currency,
            'unit': 'per_kg',
            'tariff_price': price_100_250 + (price_100_250*airline_margins[airline_id])
        },
        {
            'upper_limit': 300,
            'lower_limit': 250.1,
            'currency': currency,
            'unit': 'per_kg',
            'tariff_price': price_250_300 + (price_250_300*airline_margins[airline_id])
        },
        {
            'lower_limit': 300.1,
            'upper_limit': 500,
            'currency': currency,
            'unit': 'per_kg',
            'tariff_price': price_300_500 + (price_300_500*airline_margins[airline_id])
        }
    ]
    return weight_slabs

def format_air_freight_rate(rate, locations,airline_id):
    weight_slabs = create_weight_slabs(rate=rate,airline_id=airline_id)
    minimum_rate = 0
    if rate['MIN.'].strip():
        minimum_rate = float(rate['MIN.'].strip())
    if airline_id =='dbd3feb3-007a-4e24-873a-bc6e5e43254d' and (rate['SCR'] or '').strip()!='XPS':
        return None

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
        'service_provider_id': COGOXPRESS,
        'density_category': 'general',
        'performed_by_id': surcharge_performed_by_id,
        'procured_by_id': surcharge_performed_by_id,
        'sourced_by_id': surcharge_performed_by_id,
        'shipment_type': 'box',
        'stacking_type': 'stackable',
        'validity_start': datetime.now(),
        'validity_end': datetime.now() + timedelta(days=7),
        'source': 'freight_look',
        'length': 300,
        'breadth':300,
        'height':300,
        'meta_data': rate['meta_data'] | { 'origin':locations[rate['Loc .']]['name'] }
    }
    return rate_obj

# def read_json():
#     import json
#     f = open('/Users/ssngurjar/chakravyuh/src/services/extensions/interactions/r.json')
#     data = json.load(f)
#     f.close()
#     return data



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

    if airline_id not in airline_ids:
        return rate
    rate_obj = format_air_freight_rate(rate=rate, locations=locations,airline_id=airline_id)
    if not rate_obj:
        return rate
    rate_obj['airline_id'] = airline_id
    rate_obj['meta_data']['airline'] = airline_name
    res = create_air_freight_rate(rate_obj)
    # res = common.create_air_freight_rate(rate_obj)
    return res


def create_freight_look_rates(request):
    from services.air_freight_rate.air_celery_worker import process_freight_look_rates
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
            process_freight_look_rates.apply_async(kwargs = { 'rate': rate, 'locations': locations }, queue='fcl_freight_rate')
            # new_rate = create_air_freight_rate_api(rate=rate, locations=locations)
        except Exception as e:
            print(e)
        

    return True