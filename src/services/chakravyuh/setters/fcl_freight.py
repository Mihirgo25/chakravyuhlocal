from fastapi.encoders import jsonable_encoder
from datetime import datetime
from micro_services.client import common
from services.chakravyuh.models.fcl_freight_rate_estimation import FclFreightRateEstimation

class FclFreightVyuh():
    def __init__(self, new_rate: dict = {}, current_validities: dict = {}):
        self.new_rate = new_rate
        self.current_validities = current_validities
    
    def get_transformations_to_be_affected(self):
        price_estimations_query = FclFreightRateEstimation.select().where(
            FclFreightRateEstimation.origin_location_id << self.new_rate['origin_location_ids'],
            FclFreightRateEstimation.destination_location_id << self.new_rate['destination_location_ids'],
            FclFreightRateEstimation.container_size == self.new_rate['container_size'],
            FclFreightRateEstimation.container_type == self.new_rate['container_type'],
            FclFreightRateEstimation.schedule_type == self.new_rate['schedule_type'],
            FclFreightRateEstimation.payment_term == self.new_rate['payment_term'],
            (FclFreightRateEstimation.commodity.is_null(True) | FclFreightRateEstimation.commodity == self.new_rate['commodity']),
            (FclFreightRateEstimation.shipping_line_id.is_null(True) | FclFreightRateEstimation.shipping_line_id == self.new_rate['shipping_line_id'])
        )

        price_estimations = jsonable_encoder(list(price_estimations_query.dicts()))
        return price_estimations
    
    def get_validity_matching_current_date(self):
        matching_validity = None
        current_date =  datetime.now().date()
        for validity in self.current_validities:
            if current_date >= validity['validity_start'] and current_date <= validity['validity_end'] and validity['schedule_type'] == self.new_rate['schedule_type'] and validity['payment_term'] == self.new_rate['payment_term']:
                matching_validity = validity
                break
        return matching_validity
    
    def get_prices_sum(self, line_items, target_currency='USD'):
        total_price = 0
        for line_item in line_items:
            if line_item['currency'] != target_currency:
                total_price = total_price + common.get_money_exchange_for_fcl({"price": line_item['price'], "from_currency": line_item['currency'], "to_currency":target_currency })['price']
            else:
                total_price = total_price + line_item['price']
        return total_price

    
    def get_price_difference(self):
        current_date =  datetime.now().date()
        matching_validity = self.get_validity_matching_current_date()

        new_rate_price = self.get_prices_sum(self.new_rate['line_items'], 'USD')

        price_difference = new_rate_price

        if matching_validity and current_date >= self.new_rate['validity_start'] and current_date <= self.new_rate['validity_end']:
            current_rate_price = self.get_prices_sum(matching_validity['line_items'], 'USD')
            price_difference = (current_rate_price or 0) - (new_rate_price or 0)
        
        return price_difference
    
    def get_adjusted_price_to_add():
        print('KI')

    def set_dynamic_pricing(self):
        '''
            
        '''

        affected_transformations = self.get_transformations_to_be_affected()
        price_difference = self.get_price_difference()

        return True
