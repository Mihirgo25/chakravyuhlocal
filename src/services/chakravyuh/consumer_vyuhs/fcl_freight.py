from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation
from services.chakravyuh.models.cost_booking_estimation import CostBookingEstimation
from fastapi.encoders import jsonable_encoder
from micro_services.client import common
from datetime import datetime

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
        self.price_factor = 5

    def get_probable_rate_transformations(self, first_rate: dict={}):
        origin_location_ids = [first_rate['origin_port_id'], first_rate['origin_country_id'], first_rate['origin_trade_id']]
        destination_location_ids = [first_rate['destination_port_id'], first_rate['destination_country_id'], first_rate['destination_trade_id']]

        shipping_line_ids = []

        for freight_rate in self.freight_rates:
            shipping_line_ids.append(freight_rate['shipping_line_id'])


        transformation_query = FclFreightRateEstimation.select(
            FclFreightRateEstimation.origin_location_id,
            FclFreightRateEstimation.origin_location_type,
            FclFreightRateEstimation.destination_location_id,
            FclFreightRateEstimation.destination_location_type,
            FclFreightRateEstimation.shipping_line_id,
            FclFreightRateEstimation.commodity,
            FclFreightRateEstimation.container_size,
            FclFreightRateEstimation.container_type,
            FclFreightRateEstimation.created_at,
            FclFreightRateEstimation.updated_at,
            FclFreightRateEstimation.schedule_type,
            FclFreightRateEstimation.payment_term,
            FclFreightRateEstimation.line_items,
            FclFreightRateEstimation.id,
            FclFreightRateEstimation.status
        ).where(
            FclFreightRateEstimation.origin_location_id << origin_location_ids,
            FclFreightRateEstimation.destination_location_id << destination_location_ids,
            FclFreightRateEstimation.container_size == self.requirements['container_size'],
            FclFreightRateEstimation.container_type == self.requirements['container_type'],
            ((FclFreightRateEstimation.commodity.is_null(True)) | (FclFreightRateEstimation.commodity == self.requirements['commodity'])),
            ((FclFreightRateEstimation.shipping_line_id.is_null(True)) | (FclFreightRateEstimation.shipping_line_id << shipping_line_ids)),
            FclFreightRateEstimation.status == 'active'
        )
        transformations = jsonable_encoder(list(transformation_query.dicts()))
        return transformations
    
    def get_probable_customer_transformations(self):
        return []
    
    def get_probable_booking_data_tranformation(self, first_rate: dict={}):
        origin_location_ids = [first_rate['origin_port_id'], first_rate['origin_country_id'], first_rate['origin_trade_id']]
        destination_location_ids = [first_rate['destination_port_id'], first_rate['destination_country_id'], first_rate['destination_trade_id']]

        shipping_line_ids = []

        for freight_rate in self.freight_rates:
            shipping_line_ids.append(freight_rate['shipping_line_id'])


        transformation_query = CostBookingEstimation.select(
            CostBookingEstimation.origin_location_id,
            CostBookingEstimation.origin_location_type,
            CostBookingEstimation.destination_location_id,
            CostBookingEstimation.destination_location_type,
            CostBookingEstimation.shipping_line_id,
            CostBookingEstimation.commodity,
            CostBookingEstimation.container_size,
            CostBookingEstimation.container_type,
            CostBookingEstimation.created_at,
            CostBookingEstimation.updated_at,
            CostBookingEstimation.schedule_type,
            CostBookingEstimation.payment_term,
            CostBookingEstimation.line_items,
            CostBookingEstimation.id,
            CostBookingEstimation.status
        ).where(
            CostBookingEstimation.origin_location_id << origin_location_ids,
            CostBookingEstimation.destination_location_id << destination_location_ids,
            CostBookingEstimation.container_size == self.requirements['container_size'],
            CostBookingEstimation.container_type == self.requirements['container_type'],
            ((CostBookingEstimation.commodity.is_null(True)) | (CostBookingEstimation.commodity == self.requirements['commodity'])),
            ((CostBookingEstimation.shipping_line_id.is_null(True)) | (CostBookingEstimation.shipping_line_id << shipping_line_ids)),
            CostBookingEstimation.status == 'active'
        )
        transformations = jsonable_encoder(list(transformation_query.dicts()))
        return transformations
    
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
    
    def apply_periodic_pricing(self, lower_limit, upper_limit):
        datetime_new = datetime.now()
        hour = datetime_new.hour
        minute = datetime_new.minute
        seconds = datetime_new.second
        price_range = upper_limit - lower_limit
        total_price_points = price_range / self.price_factor

        total_seconds_in_day = 24 * 60 * 60

        total_seconds_passed = (hour * 60 * 60) + (minute * 60) + seconds

        if total_price_points < 1:
            total_price_points = 1
        
        seconds_per_point = total_seconds_in_day / total_price_points

        current_time_point = (total_seconds_passed / seconds_per_point) + 1

        price_delta = current_time_point * self.price_factor

        final_price = lower_limit + price_delta

        return int(final_price)

    
    def get_line_item_price(self, line_item, tranformed_lineitem):
        lower_limit = tranformed_lineitem['lower_limit']
        upper_limit = tranformed_lineitem['upper_limit']
        currency = tranformed_lineitem['currency']

        if line_item['currency'] != currency:
            lower_limit = common.get_money_exchange_for_fcl({"price": lower_limit, "from_currency": currency, "to_currency": line_item['currency'] })['price']
            upper_limit = common.get_money_exchange_for_fcl({"price": upper_limit, "from_currency": currency, "to_currency": line_item['currency'] })['price']
        
        lower_limit = int(lower_limit)
        upper_limit = int(upper_limit)
        
        line_item['price'] = self.apply_periodic_pricing(lower_limit, upper_limit)
        
        if line_item['price'] >= 200:
            line_item['price'] = round(line_item['price']/5) * 5
        else:
            line_item['price'] = round(line_item['price'])
        
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
    

    def apply_booking_data_transformation(self, rate, probable_booking_data_transformations):
        
        probable_transformation_to_apply = self.get_most_eligible_rate_transformation(probable_booking_data_transformations)
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
        

    def apply_transformation(self, rate, probable_transformations, probable_customer_transformations,probable_booking_data_transformations):
        rate_specific_transformations = []
        for pt in probable_transformations:
            if (not pt['shipping_line_id'] or pt['shipping_line_id'] == rate['shipping_line_id']):
                rate_specific_transformations.append(pt)
        new_rate = rate
        if len(probable_booking_data_transformations)>0:
            new_rate=self.apply_booking_data_transformation(rate=new_rate, probable_booking_data_transformations=probable_booking_data_transformations)
            return new_rate
        
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

        probable_booking_data_transformations=self.get_probable_booking_data_tranformation(first_rate)

        new_freight_rates = []

        for freight_rate in self.freight_rates:
            new_freight_rate = self.apply_transformation(
                rate=freight_rate, 
                probable_transformations=probable_transformations,
                probable_customer_transformations=probable_customer_transformations,
                probable_booking_data_transformations=probable_booking_data_transformations
            )
            new_freight_rates.append(new_freight_rate)
        
        return new_freight_rates