from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from configs.fcl_customs_rate_constants import LOCATION_HIERARCHY
from micro_services.client import maps
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID
from configs.fcl_freight_rate_constants import DEFAULT_SERVICE_PROVIDER_ID
from celery_worker import create_fcl_customs_rate_delay
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

def get_zone_wise_rate_query(request):
    location_data = maps.list_locations({'includes':{'zone_id':True}, 'filters':{'id': request.get('port_id')}})['list']
    if location_data:
        zone_id = location_data[0].get('zone_id')

        zone_wise_rates = FclCustomsRate.select(
            FclCustomsRate.customs_line_items,
            FclCustomsRate.service_provider_id,
            FclCustomsRate.importer_exporter_id,
            FclCustomsRate.location_type,
            FclCustomsRate.location_id
            ).where(
            FclCustomsRate.zone_id == zone_id,
            FclCustomsRate.country_id == request.get('country_id'),
            FclCustomsRate.container_size == request.get('container_size'),
            FclCustomsRate.container_type == request.get('container_type'),
            FclCustomsRate.trade_type == request.get('trade_type'),
            FclCustomsRate.is_customs_line_items_error_messages_present == False,
            FclCustomsRate.rate_not_available_entry == False,
            FclCustomsRate.mode == 'manual',
            ((FclCustomsRate.commodity == request.get('commodity')) | (FclCustomsRate.commodity.is_null(True))),
            ((FclCustomsRate.importer_exporter_id == request.get('importer_exporter_id')) | (FclCustomsRate.importer_exporter_id.is_null(True)))
        )
        custom_rates = jsonable_encoder(list(zone_wise_rates.dicts()))
        return custom_rates
    return []

def get_zone_average_customs_rate(request):
    customs_rates = get_zone_wise_rate_query(request)
    if customs_rates:
        for rate in customs_rates:
            line_items = rate['customs_line_items']
            code_prices = {}
            units = {}

            for line_item in line_items:
                code = line_item['code']
                price = line_item['price']
                unit = line_item['unit']
                
                if code in code_prices:
                    code_prices[code].append(price)
                else:
                    code_prices[code] = [price]
                units[code] = unit
            
        average_items = []
        currency = customs_rates[0]['customs_line_items'][0].get('currency')

        for code, prices in code_prices.items():
            average_price = sum(prices) / len(prices)
            average_item = {
                'code': code,
                'unit': units[code],
                'price': average_price,
                'remarks': [],
                'currency': currency,
                'location_id': None
            }
            average_items.append(average_item)

        rates = sorted(customs_rates, key = lambda x: LOCATION_HIERARCHY[x['location_type']] )
        predicted_customs_rate = rates[0]
        predicted_customs_rate['customs_line_items'] = average_items
        predicted_customs_rate['importer_exporter_id'] = None
        predicted_customs_rate['location_id'] = request.get('port_id')
        create_params = get_create_params(request, predicted_customs_rate['customs_line_items'])

        create_fcl_customs_rate_delay.apply_async(kwargs = {'request':create_params}, queue = 'low')
        return [predicted_customs_rate]
    else:
        return []

def get_create_params(request, line_items):
    return {
        'location_id':request.get('port_id'),
        'trade_type' : request.get('trade_type'),
        'container_size' : request.get('container_size'),
        'container_type' : request.get('container_type'),
        'commodity' :  request.get('commodity'),
        'service_provider_id' : DEFAULT_SERVICE_PROVIDER_ID,
        'procured_by_id' : DEFAULT_USER_ID,
        'sourced_by_id' : DEFAULT_USER_ID,
        'customs_line_items' : line_items,
        'performed_by_id' : DEFAULT_USER_ID,
        'mode' : 'predicted',
        'accuracy' : 75,
        'rate_type' : DEFAULT_RATE_TYPE
    }