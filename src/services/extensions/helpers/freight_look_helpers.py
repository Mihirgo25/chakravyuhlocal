from micro_services.client import  maps

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