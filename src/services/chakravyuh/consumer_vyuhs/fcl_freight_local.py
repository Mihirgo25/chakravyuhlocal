from services.chakravyuh.models.fcl_freight_rate_local_estimation import FclFreightRateLocalEstimation
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_local import create_fcl_freight_rate_local
from configs.fcl_freight_rate_constants import DEFAULT_SERVICE_PROVIDER_ID
from configs.global_constants import HAZ_CLASSES
from micro_services.client import maps
from fastapi.encoders import jsonable_encoder
import copy

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
        commodity = request[0].get('commodity') if request[0].get('commodity') in HAZ_CLASSES else None
        estimated_rate_query = FclFreightRateLocalEstimation.select(
            FclFreightRateLocalEstimation.location_id,
            FclFreightRateLocalEstimation.location_type,
            FclFreightRateLocalEstimation.trade_type,
            FclFreightRateLocalEstimation.line_items
        ).where(
            FclFreightRateLocalEstimation.location_id << location_ids,
            FclFreightRateLocalEstimation.trade_type << ['import','export'],
            FclFreightRateLocalEstimation.container_size == request[0].get("container_size"),
            FclFreightRateLocalEstimation.container_type == request[0].get("container_type"),
            FclFreightRateLocalEstimation.commodity == commodity
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
        
        import_rate, export_rate = self.get_most_eligible_rate_transformation(local_freight_line_items)

        for param in request:
            local_freight_param = self.set_create_fcl_freight_rate_local(param, from_rate_card, import_rate, export_rate)
            if local_freight_param and isinstance(local_freight_param, dict):
                local_freight_rates.append(local_freight_param)
            elif local_freight_param and isinstance(local_freight_param, list):
                local_freight_rates.extend(local_freight_param)

        return list(filter(None, local_freight_rates))

    def sort_items(self, item: dict = {}):
        priority = self.location_type_priority[item['location_type']]
        return priority
    
    def get_most_eligible_rate_transformation(self, probable_transformations: list =[]):
        import_items = []
        export_items = []

        for transformation in probable_transformations:
            if transformation.get('trade_type') == 'import':
                import_items.append(transformation)
            else:
                export_items.append(transformation)

        import_items.sort(key = self.sort_items)
        export_items.sort(key = self.sort_items)

        return import_items, export_items

    def set_local_line_items(self, local_rate):
        line_items = []
        rate = copy.deepcopy(local_rate)
        for line_item in rate.get('line_items'):
            local_price = round((line_item['upper_price'] + line_item['lower_price'])/2)
            if local_price > 0:
                line_item['price'] = local_price + (5 - local_price%10) if local_price%10 <= 5 else (local_price + (10 - local_price%10))
            else:
                line_item['price'] = local_price
            del line_item['upper_price']
            del line_item['lower_price']
            line_items.append(line_item)
        rate['line_items'] = line_items
        return rate

    def set_create_fcl_freight_rate_local(self, param, from_rate_card, import_rate, export_rate):
        local_freight_common_param = {
                'container_size': param.get('container_size'),
                'container_type': param.get('container_type'),
                'commodity': param.get('commodity') if param.get('commodity') in HAZ_CLASSES else None,
                'shipping_line_id': param.get('shipping_line_id'),
                'service_provider_id': DEFAULT_SERVICE_PROVIDER_ID,
                'source':'predicted',
                'shipping_line_id' : param.get('shipping_line_id')
            }

        if from_rate_card:
            origin_local_param = local_freight_common_param | {'trade_type':'export', 'port_id':param.get('origin_port_id'), 'main_port_id':param.get('origin_main_port_id')}
            destination_local_param = local_freight_common_param | {'trade_type':'import', 'port_id':param.get('destination_port_id'), 'main_port_id':param.get('destination_main_port_id')}

            created_rate_params = []
            for trade_type in ['import', 'export']:
                if trade_type == 'import':
                    local_freight_rate = self.create_fcl_freight_local_rate(destination_local_param, import_rate)
                else:
                    local_freight_rate = self.create_fcl_freight_local_rate(origin_local_param, export_rate)
                created_rate_params.append(local_freight_rate)
        else:
            if param.get('trade_type') == 'import':
                local_freight_eligible_rate = import_rate
            else:
                local_freight_eligible_rate = export_rate
            local_freight_create_param = local_freight_common_param | {'trade_type':param.get('trade_type'), 'port_id':param.get('port_id'), 'main_port_id':param.get('main_port_id')}

            created_rate_params = self.create_fcl_freight_local_rate(local_freight_create_param, local_freight_eligible_rate)
        
        return created_rate_params
            
    def create_fcl_freight_local_rate(self, rate_param, local_freight_eligible_rate):
        if local_freight_eligible_rate:
            local_freight_eligible_rate = self.set_local_line_items(local_freight_eligible_rate[0])
            rate_param = rate_param | {'data':{'line_items':local_freight_eligible_rate.get('line_items') ,'plugin': None, 'detention': None, 'demurrage': None}, 'line_items':local_freight_eligible_rate.get('line_items'), 'rate_not_available_entry':False}
            rate_param['id'] = create_fcl_freight_rate_local(rate_param).get('id')
        else:
            rate_param = None
        return rate_param