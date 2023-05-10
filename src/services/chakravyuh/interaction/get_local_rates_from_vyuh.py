from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local
from configs.global_constants import HAZ_CLASSES
from configs.fcl_freight_rate_constants import DEFAULT_SERVICE_PROVIDER_ID
from services.chakravyuh.consumer_vyuhs.fcl_freight_local import FclFreightLocalVyuh
from micro_services.client import maps

def get_local_rates_from_vyuh(request):
    if request.get('main_port_id'):
        main_port_id = request['main_port_id']
    else:
        location_data = maps.list_locations_mapping({'location_id':request['port_id'],'type':['main_ports']})
        if location_data and isinstance(location_data, dict):
            main_port_id = location_data['list'][0].get('id') if len(location_data['list']) > 0 else None
        else:
            main_port_id = None

    fcl_freight_local_vyuh = FclFreightLocalVyuh()
    local_freight_rates = fcl_freight_local_vyuh.get_eligible_local_estimated_rate(request)
    if local_freight_rates:
        for local_rate in local_freight_rates['line_items']:
            local_price = round((local_rate['upper_price'] + local_rate['lower_price'])/2)
            if local_price > 0:
                local_rate['price'] = local_price + (5 - local_price%10) if local_price%10 <= 5 else (local_price + (10 - local_price%10))
            else:
                local_price['price'] = local_price
            del local_rate['upper_price']
            del local_rate['lower_price']

        local_freight_create_params = {
            'trade_type': request.get('trade_type'),
            'port_id': request.get('port_id'),
            'main_port_id': main_port_id,
            'container_size': request.get('container_size'),
            'container_type': request.get('container_type'),
            'commodity': request.get('commodity') if request.get('commodity') in HAZ_CLASSES else None,
            'shipping_line_id': request.get('shipping_line_id'),
            'service_provider_id': DEFAULT_SERVICE_PROVIDER_ID,
            'data': local_freight_rates,
            'line_items':local_freight_rates.get('line_items'),
            'source':'predicted',
            'shipping_line_id':request.get('shipping_line_id')
        }
        local_freight_create_params['id'] = create_fcl_freight_rate_local(local_freight_create_params).get('id')
        return [local_freight_create_params]
    else:
        return []