from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
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
        self.default_transformed_lineitem = {
            'lower_limit': 2000,
            'upper_limit': 2500,
            'currency': 'USD',
        }

    def get_probable_rate_transformations(self, first_rate: dict={}):
        origin_location_ids = [first_rate['origin_port_id'], first_rate['origin_country_id'], first_rate['origin_trade_id']]
        destination_location_ids = [first_rate['destination_port_id'], first_rate['destination_country_id'], first_rate['destination_trade_id']]

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
            line_item['price'] = random.randrange(start=int(lower_limit), stop=int(upper_limit + 1))
        
        return line_item

    
    def apply_rate_transformation(self, rate, probable_transformations):
        probable_transformation_to_apply = self.get_most_eligible_rate_transformation(probable_transformations)

        validities = rate['validities'] or []

        new_validities = []

        for validity in validities:

            line_items = validity['line_items']

            transformation_items = probable_transformation_to_apply['line_items']

            new_lineitems = []
            for line_item in line_items:
                transformed_line_item = self.get_lineitem(code=line_item['code'], items=transformation_items)
                if transformed_line_item:
                    adjusted_lineitem = self.get_line_item_price(line_item=line_item, tranformed_lineitem=transformed_line_item)
                    new_lineitems.append(adjusted_lineitem)
                else:
                    new_lineitems.append(line_item)
        
            validity['line_items'] = new_lineitems
            new_validities.append(validity)
        
        rate['validities'] = new_validities

        return rate
    
    def apply_default_transformation(self, rate):
        validities = rate['validities'] or []
        new_validities = []
        for validity in validities:
            line_items = validity['line_items']
            new_lineitems = []
            for line_item in line_items:
                if line_item['code'] == 'BAS' and line_item['price'] < 2000:
                    transformed_line_item = self.default_transformed_lineitem
                    adjusted_lineitem = self.get_line_item_price(line_item=line_item, tranformed_lineitem=transformed_line_item)
                    new_lineitems.append(adjusted_lineitem)
                else:
                    new_lineitems.append(line_item)
            
            validity['line_items'] = new_lineitems
            new_validities.append(validity)
        rate['validities'] = new_validities
        return rate

    def apply_transformation(self, rate, probable_transformations, probable_customer_transformations):
        rate_specific_transformations = []
        for pt in probable_transformations:
            if (not pt['shipping_line_id'] or pt['shipping_line_id'] == rate['shipping_line_id']):
                rate_specific_transformations.append(pt)
        new_rate = rate
        if len(rate_specific_transformations) > 0:
            new_rate = self.apply_rate_transformation(rate=rate, probable_transformations=rate_specific_transformations)
        else:
            new_rate = self.apply_default_transformation(rate=rate)
            
        if len(probable_customer_transformations) > 0:
            new_rate = self.apply_customer_transformation(rate=new_rate, probable_customer_transformations=probable_customer_transformations)

        return new_rate

    def apply_dynamic_pricing(self):

        if len(self.freight_rates) == 0:
            return self.freight_rates
        
        
        first_rate = self.freight_rates[0]

        probable_transformations = self.get_probable_rate_transformations(first_rate)

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