from services.chakravyuh.models.fcl_freight_rate_local_estimation import FclFreightRateLocalEstimation
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local
from configs.fcl_freight_rate_constants import DEFAULT_SERVICE_PROVIDER_ID
from configs.global_constants import HAZ_CLASSES
from micro_services.client import maps
from fastapi.encoders import jsonable_encoder

class FclFreightLocalVyuh():
    def __init__(self, rates: list = []):
        self.rates = rates
        self.location_type_priority = {
            'country': 1,
            'trade': 2,
        }
    def check_fulfilment_ratio(self):
        return 100

    def apply_dynamic_price(self):
        print(self.rates)

    def get_local_estimated_rate_query(self, request, location_ids):
        estimated_rate_query = FclFreightRateLocalEstimation.select(
            FclFreightRateLocalEstimation.location_type,
            FclFreightRateLocalEstimation.trade_type,
            FclFreightRateLocalEstimation.line_items
        ).where(
            FclFreightRateLocalEstimation.location_id << location_ids,
            FclFreightRateLocalEstimation.trade_type << ['import','export'],
            FclFreightRateLocalEstimation.container_size == request[0].get("container_size"),
            FclFreightRateLocalEstimation.container_type == request[0].get("container_type"),
            FclFreightRateLocalEstimation.commodity == request[0].get('commodity')
        )
        return estimated_rate_query

    def get_most_eligible_local_estimated_rate(self, request, port_ids):
        locations_data = maps.list_locations({'filters': {'id': port_ids}})
        location_ids = []

        if locations_data and isinstance(locations_data, dict):
            for data in locations_data['list']:
                location_ids.extend([data.get('trade_id'),data.get('country_id')])

        local_freight_query = self.get_local_estimated_rate_query(request, location_ids)
        local_freight_line_items = jsonable_encoder(list(local_freight_query.dicts()))
        local_freight_rates = []

        for param in request:
            local_freight_eligible_rate = self.get_most_eligible_rate_transformation(local_freight_line_items)

            if local_freight_eligible_rate:
                local_freight_eligible_rate = self.set_local_line_items(local_freight_eligible_rate)

                local_freight_create_params = {
                    'trade_type': param.get('trade_type'),
                    'port_id': param.get('port_id'),
                    'main_port_id':param.get('main_port_id'),
                    'container_size': param.get('container_size'),
                    'container_type': param.get('container_type'),
                    'commodity': param.get('commodity') if param.get('commodity') in HAZ_CLASSES else None,
                    'shipping_line_id': param.get('shipping_line_id'),
                    'service_provider_id': DEFAULT_SERVICE_PROVIDER_ID,
                    'data': local_freight_eligible_rate,
                    'line_items':local_freight_eligible_rate.get('line_items'),
                    'source':'predicted',
                    'shipping_line_id':param.get('shipping_line_id')
                }
                local_freight_create_params['id'] = create_fcl_freight_rate_local(local_freight_create_params).get('id')
                print(local_freight_create_params, 'local params')
            else:
                local_freight_create_params = {}
            
            local_freight_rates.append(local_freight_create_params)
        
        return local_freight_rates

    def sort_items(self, item: dict = {}):
        priority = 0
        priority = priority + self.location_type_priority[item['location_type']]
        return priority
    
    def get_most_eligible_rate_transformation(self, probable_transformations: list =[]):
        probable_transformations.sort(key = self.sort_items)
        return probable_transformations[0]

    def set_local_line_items(self, local_rate):
        line_items = []
        for line_item in local_rate.get('line_items'):
            local_price = round((line_item['upper_price'] + line_item['lower_price'])/2)
            if local_price > 0:
                line_item['price'] = local_price + (5 - local_price%10) if local_price%10 <= 5 else (local_price + (10 - local_price%10))
            else:
                line_item['price'] = local_price
            del line_item['upper_price']
            del line_item['lower_price']
            line_items.append(line_item)
        local_rate['line_items'] = line_items
        return local_rate