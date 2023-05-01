from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from micro_services.client import maps
from fastapi.encoders import jsonable_encoder
from micro_services.client import common
import random

class FclFreightVyuh():
    def __init__(self, freight_rates: list = [], requirements: dict = {}):
        self.freight_rates = freight_rates
        self.requirements = requirements
        self.locaton_type_priority = {
            'seaport': 1,
            'country': 2,
            'trade': 3,
        }
    
    def get_location_details(self):
        origin_port_id = self.requirements['origin_port_id']
        destination_port_id = self.requirements['destination_port_id']
        locations_description = maps.list_locations({'filters': {'id': [origin_port_id, destination_port_id] }})

        if locations_description and isinstance(locations_description, dict):
            locations_description = locations_description['list']
        else:
            locations_description = []
        locations_hash = {}
        for loc in locations_description:
            locations_hash[loc['id']] = loc

        return locations_hash

    def get_probable_rate_transformations(self):
        location_details = self.get_location_details()
        origin_details = location_details[self.requirements['origin_port_id']]
        destination_details = location_details[self.requirements['destination_port_id']]
        origin_location_ids = [origin_details['id'], origin_details['country_id'], origin_details['trade_id']]
        destination_location_ids = [destination_details['id'], destination_details['country_id'], destination_details['trade_id']]

        shipping_line_ids = []

        for freight_rate in self.freight_rates:
            shipping_line_ids.append(freight_rate['shipping_line_id'])


        transformation_query = FclFreightRateEstimation.select().where(
            FclFreightRateEstimation.origin_location_id << origin_location_ids,
            FclFreightRateEstimation.destination_location_id << destination_location_ids,
            FclFreightRateEstimation.container_size == self.requirements['container_size'],
            FclFreightRateEstimation.container_type == self.requirements['container_type'],
            ((FclFreightRateEstimation.commodity.is_null(True)) | (FclFreightRateEstimation.commodity == self.requirements['commodity'])),
            ((FclFreightRateEstimation.shipping_line_id.is_null(True)) | (FclFreightRateEstimation.shipping_line_id << shipping_line_ids)),
        )
        transformations = jsonable_encoder(list(transformation_query.dicts()))
        return transformations
    
    def get_probable_customer_transformations(self):
        return []
    
    def get_most_eligible_customer_transformation(self, probable_customer_transformations):
        return probable_customer_transformations[0]

    
    def apply_customer_transformation(self, rate, probable_customer_transformations):
        customer_transformation_to_apply = self.get_most_eligible_customer_transformation(probable_customer_transformations)
        return rate
    
    def sort_items(self, item: dict = {}):
        priority = 0
        priority = priority + self.locaton_type_priority[item['origin_location_type']]
        if not item.get('shipping_line_id'):
            priority = priority + 1
        return priority
    
    def get_most_eligible_rate_transformation(self, probable_transformations: list =[]):
        probable_transformations.sort(key = self.sort_items)
        return probable_transformations[0]
    
    def get_lineitem(self, code: str, items: list = []):
        line_item = None
        for item in items:
            if item['code'] == code:
                line_item = item
                break

        return line_item 
    
    def get_line_item_price(self, line_item, tranformed_lineitem):
        lower_limit = tranformed_lineitem['lower_limit']
        upper_limit = tranformed_lineitem['upper_limit']
        currency = tranformed_lineitem['currency']

        if line_item['currency'] != currency:
            lower_limit = common.get_money_exchange_for_fcl({"price": lower_limit, "from_currency": currency, "to_currency": line_item['currency'] })['price']
            upper_limit = common.get_money_exchange_for_fcl({"price": upper_limit, "from_currency": currency, "to_currency": line_item['currency'] })['price']
        
        if line_item['price'] < lower_limit or line_item['price'] > upper_limit:
            line_item['price'] = random.randrange(start=lower_limit, stop=upper_limit)
        
        return line_item

    
    def apply_rate_transformation(self, rate, probable_transformations):
        probable_transformation_to_apply = self.get_most_eligible_rate_transformation(probable_transformations)
        line_items = rate['line_items']

        transformation_items = probable_transformation_to_apply['line_items']

        new_lineitems = []
        for line_item in line_items:
            transformed_line_item = self.get_lineitem(code=line_item['code'], items=transformation_items)
            if transformed_line_item:
                adjusted_lineitem = self.get_line_item_price(line_item=line_item, tranformed_lineitem=transformed_line_item)
                new_lineitems.append(adjusted_lineitem)
            else:
                new_lineitems.append(line_item)
        
        rate['line_items'] = new_lineitems

        return rate

    def apply_transformation(self, rate, probable_transformations, probable_customer_transformations):
        rate_specific_transformations = []
        for pt in probable_transformations:
            if (not pt['shipping_line_id'] or pt['shipping_line_id'] == rate['shipping_line_id']):
                rate_specific_transformations.append(pt)
        new_rate = rate
        if len(rate_specific_transformations) > 0:
            new_rate = self.apply_rate_transformation(rate=rate, probable_transformations=rate_specific_transformations)
        if len(probable_customer_transformations) > 0:
            new_rate = self.apply_customer_transformation(rate=new_rate, probable_customer_transformations=probable_customer_transformations)

        return new_rate

    def apply_dynamic_pricing(self):

        probable_transformations = self.get_probable_rate_transformations()

        probable_customer_transformations = self.get_probable_customer_transformations()

        new_freight_rates = []

        for freight_rate in self.freight_rates:
            new_freight_rate = self.apply_transformation(
                rate=freight_rate, 
                probable_transformations=probable_transformations,
                probable_customer_transformations=probable_customer_transformations,
            )
            new_freight_rates.append(new_freight_rate)
        
        return new_freight_rates