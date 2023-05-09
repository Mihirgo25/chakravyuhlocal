from services.chakravyuh.consumer_vyuhs.fcl_freight_local import FclFreightLocalVyuh
from micro_services.client import maps

def get_local_rates_from_vyuh(local_rate_params):
    port_ids = [param.get('port_id') for param in local_rate_params]
    main_ports_data = maps.list_locations_mapping({'location_id':port_ids,'type':['main_ports']})
    main_port_dict = {}
    
    if main_ports_data and isinstance(main_ports_data, dict):
        for data in main_ports_data['list']:
            main_port_dict[data.get('country_id')] = data.get('port_id')
            
    for param in local_rate_params:
        param['main_port_id'] = main_port_dict.get(param.get('port_id'))

    fcl_freight_local_vyuh = FclFreightLocalVyuh()
    local_freight_rates = fcl_freight_local_vyuh.get_most_eligible_local_estimated_rate(local_rate_params, port_ids)
    return local_freight_rates