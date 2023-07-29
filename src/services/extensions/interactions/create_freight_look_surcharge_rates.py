
from services.extensions.helpers.freight_look_helpers import get_locations,create_proper_json
from services.air_freight_rate.constants.air_freight_rate_constants import DEFAULT_AIRLINE_ID, SURCHARGE_SERVICE_PROVIDERS
from micro_services.client import maps
from services.extensions.constants.general import commodity_mappings, commodity_type_mappings, surcharge_charges_mappings, surcharge_performed_by_id
from configs.global_constants import  DEFAULT_SERVICE_PROVIDER_ID, DEFAULT_PROCURED_BY_ID
from services.air_freight_rate.interactions.create_air_freight_rate_surcharge import create_air_freight_rate_surcharge
airline_hash = {}
def create_freight_look_surcharge_rate(request):
    from celery_worker import process_freight_look_surcharge_rate_in_delay
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
        try:
            process_freight_look_surcharge_rate_in_delay.apply_async(kwargs = { 'rate': rate, 'locations': locations }, queue='fcl_freight_rate')
        except Exception as e:
            print(e)

def create_surcharge_rate_api(rate,locations):
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
    surcharge_params = format_surcharge_rate(rate,locations,airline_id)
    if surcharge_params and surcharge_params.get('line_items'):
        for sp in SURCHARGE_SERVICE_PROVIDERS:
            surcharge_params['service_provider_id'] = sp
            create_air_freight_rate_surcharge(surcharge_params)



def format_surcharge_rate(rate,locations,airline_id):
    commodity = commodity_mappings.get((rate['SCR'] or '').strip())
    commodity_type = commodity_type_mappings.get((rate['SCR'] or '').strip())
    if not commodity or not commodity_type:
        return None
    line_items = []

    for key, value in rate.items():
        if key in ['SSC','FSC/MIN','XRAY/MIN','MISC/MIN','CTG/MIN','AMS-M/AWB','AMS-M/HAWB','AMS-E/AWB','AMS-E/HAWB']:
            line_item = build_line_item(value,key)
            if line_item:
                line_items.append(line_item)


    surcharge =  {
        'origin_airport_id': locations[rate['Loc .']]['id'],
        'destination_airport_id': rate['destination_airport_id'],
        'commodity': commodity,
        'commodity_type': commodity_type,
        'operation_type': 'passenger',
        'service_provider_id': DEFAULT_SERVICE_PROVIDER_ID,
        'performed_by_id': surcharge_performed_by_id,
        'procured_by_id': surcharge_performed_by_id,
        'sourced_by_id': surcharge_performed_by_id,
        'line_items':line_items,
        'airline_id':airline_id
    }
    return surcharge

def build_line_item(line_item_price,code):
    line_item_price = line_item_price.strip()
    if not line_item_price:
        return
    min_price = 0
    price = 0
    unit = 'per_kg'
    code = surcharge_charges_mappings[code]
    if line_item_price.find('/')!=-1:
        index = line_item_price.find('/') +1
        min_price = line_item_price[index:len(line_item_price)]
        min_price = min_price.strip()
        min_price = float(min_price)
    
    if line_item_price.find('C')!=-1:
        index = line_item_price.find('C')
        price = line_item_price[0:index]
        price = price.strip()
        price = float(price)
    elif line_item_price.find('G')!=-1:
        index = line_item_price.find('G')
        price = line_item_price[0:index]
        price = price.strip()
        price = float(price)
        unit = 'per_kg_gross'
    else:
        price = line_item_price.strip()
        price = float(price)
        unit = 'per_package'
    if code == 'CTS':
        unit = 'per_kg_gross'
    
    if code in ['HAMS','EAMS','EHAMS']:
        unit = 'per_document' 
    
    if code == 'AMS':
        unit = 'per_awb'

    line_item = {'code':code,'unit':unit,'price':price,'min_price':min_price,'currency':'INR','remarks':[]}
    return line_item
    
    
# create_freight_look_surcharge_rate(request)
    

