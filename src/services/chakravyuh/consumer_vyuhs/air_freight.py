from services.chakravyuh.models.air_freight_rate_estimation import AirFreightRateEstimation
from fastapi.encoders import jsonable_encoder
from configs.air_freight_rate_constants import AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
from micro_services.client import common
from random import randint

class AirFreightVyuh():
    def __init__(self, freight_rates: list = [],requirements: dict = {}):
        self.freight_rates = freight_rates
        self.requirements = requirements
        
    def get_probable_rate_transformations(self):
        origin_location_ids = [self.requirements['origin_country_id']]
        destination_location_ids = [self.requirements['destination_country_id']]

        airline_ids = []

        for freight_rate in self.freight_rates:
            airline_ids.append(freight_rate['airline'])

        transformation_query = AirFreightRateEstimation.select().where(
            AirFreightRateEstimation.origin_location_id << origin_location_ids,
            AirFreightRateEstimation.destination_location_id << destination_location_ids,
            ((AirFreightRateEstimation.operation_type == self.requirements['operation_type']) | (AirFreightRateEstimation.operation_type.is_null(True))),
            ((AirFreightRateEstimation.stacking_type.is_null(True)) | (AirFreightRateEstimation.stacking_type == self.requirements['stacking_type'])),
            ((AirFreightRateEstimation.shipment_type.is_null(True)) | (AirFreightRateEstimation.shipment_type == self.requirements['shipment_type']))

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
        if not item.get('airline_id'):
            priority = priority + 1
        return priority
    
    def get_most_eligible_rate_transformation(self, probable_transformations: list =[]):
        probable_transformations.sort(key = self.sort_items)
        return probable_transformations[0]
    
    def get_modified_weight_slab(self,price,weight_slab,currency):

        required_weight_slab = {
             'lower_limit':weight_slab['lower_limit'],
                'upper_limit':weight_slab['upper_limit'],
                'tariff_price':price,
                'currency':currency,
                'unit':'per kg'
        }
        lower_limit = weight_slab['lower_limit_price']
        upper_limit = weight_slab['upper_limit_price']
        if weight_slab['currency']!=currency:
            lower_limit = common.get_money_exchange_for_fcl({"price": weight_slab['lower_limit_price'], "from_currency": weight_slab['currency'], "to_currency": currency })['price']
            upper_limit = common.get_money_exchange_for_fcl({"price": weight_slab['upper_limit_price'], "from_currency": weight_slab['currency'], "to_currency": currency })['price']
        
        if price >= lower_limit and price <= upper_limit:
            return required_weight_slab
        
        required_weight_slab['tariff_price'] = randint(lower_limit,upper_limit)
        return required_weight_slab


    def get_weight_slab(self,price,weight_slabs,currency):
        weight = self.requirements.get('weight')
        for weight_slab in weight_slabs:
            if weight >= weight_slab['lower_limt'] and weight <= weight_slab['upper_limit']:
                weight_slab = self.get_modified_weight_slab(price,weight_slab,currency)
                return weight_slab

    def apply_rate_transformation(self, rate, probable_transformations):
        probable_transformation_to_apply = self.get_most_eligible_rate_transformation(probable_transformations)
        weight_slab = self.get_weight_slab(rate.get('price'),probable_transformation_to_apply.get('weight_slabs'),rate.get('currency'))
        rate['weight_slab'] = weight_slab
        return rate
        

    def apply_transformation(self,rate,probable_transformations, probable_customer_transformations):
        rate_specific_transformations = []
        for pt in probable_transformations:
            if (not pt['airline_id'] or pt['airline_id'] == rate['airline_id']):
                rate_specific_transformations.append(pt)
        if len(rate_specific_transformations) > 0:
            new_rate = self.apply_rate_transformation(rate ,probable_transformations=rate_specific_transformations)
        else:
            new_rate = self.apply_rate_transformation(rate,probable_transformations=probable_transformations)
        
        if len(probable_customer_transformations) > 0:
            new_rate = self.apply_customer_transformation(rate=new_rate, probable_customer_transformations=probable_customer_transformations)

        return new_rate['weight_slabs']

    def apply_dynamic_pricing(self):

        probable_transformations = self.get_probable_rate_transformations()
 
        if len(probable_transformations)==0:
            return []
        probable_customer_transformations = self.get_probable_customer_transformations()

        new_freight_rates = []

        for freight_rate in self.freight_rates:
            new_freight_rate = self.apply_transformation(
                    rate = freight_rate,
                    probable_transformations=probable_transformations,
                    probable_customer_transformations=probable_customer_transformations,
                )
            
        
        return new_freight_rate
    
    