from services.chakravyuh.models.air_freight_rate_estimation import AirFreightRateEstimation
from fastapi.encoders import jsonable_encoder
from configs.air_freight_rate_constants import AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
from micro_services.client import common
import random

class AirFreightVyuh():
    def __init__(self, requirements):
        self.requirements = requirements
        self.locaton_type_priority = {
            'airport': 1,
            'cluster': 2,
        }


    def get_probable_rate_transformations(self):
        # get cluster main airport id
        destination_cluster_id = self.requirements()
        origin_location_ids = [self.requirements['origin_airport_id']]
        destination_location_ids = [self.requirements['destination_airport_id'],destination_cluster_id]


        transformation_query = AirFreightRateEstimation.select().where(
            AirFreightRateEstimation.origin_location_id << origin_location_ids,
            AirFreightRateEstimation.destination_location_id << destination_location_ids,
            AirFreightRateEstimation.commodity == self.requirements['commodity'],
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
        if not item.get('airline_id'):
            priority = priority + 1
        return priority
    
    def get_most_eligible_rate_transformation(self, probable_transformations: list =[]):
        probable_transformations.sort(key = self.sort_items)
        return probable_transformations[0]
    

    def apply_rate_transformation(self,  probable_transformations):
        probable_transformation_to_apply = self.get_most_eligible_rate_transformation(probable_transformations)

        required_weight = self.get_chargable_weight()
        weight_slab = self.get_weight_slab(required_weight,probable_transformation_to_apply['weight_slabs'])
        rate = weight_slab['tariff_price']
        if weight_slab['currency'] != self.requirements['currency']:
            rate = common.get_money_exchange_for_fcl({"price": rate, "from_currency": self.requirements['currency'], "to_currency": weight_slab['currency'] })['price']
        
        self.requirements['estimated_rate'] = rate
        

    def apply_transformation(self, probable_transformations, probable_customer_transformations):
        rate_specific_transformations = []
        for pt in probable_transformations:
            if (not pt['airline_id'] or pt['airline_id'] == self.requirements['airline_id']):
                rate_specific_transformations.append(pt)
        if len(rate_specific_transformations) > 0:
            new_rate = self.apply_rate_transformation( probable_transformations=rate_specific_transformations)
        else:
            new_rate = self.apply_rate_transformation(probable_transformations=probable_transformations)
            
        if len(probable_customer_transformations) > 0:
            new_rate = self.apply_customer_transformation(rate=new_rate, probable_customer_transformations=probable_customer_transformations)

        return self.requirements

    def apply_dynamic_pricing(self):

        probable_transformations = self.get_probable_rate_transformations()

        probable_customer_transformations = self.get_probable_customer_transformations()


        new_freight_rate = self.apply_transformation(
                probable_transformations=probable_transformations,
                probable_customer_transformations=probable_customer_transformations,
            )
        
        return new_freight_rate
    
    def get_chargable_weight(self):
        volumetric_weight = self.requirements.get('volume') * AIR_STANDARD_VOLUMETRIC_WEIGHT_CONVERSION_RATIO
        chargeable_weight = max(volumetric_weight,self.requirements.get('weight'))
        return chargeable_weight
    
    def get_required_weight_slab(required_weight,weight_slabs):
        for weight_slab in weight_slabs:
            if weight_slab['lower_limt']<=required_weight and weight_slab['upper_limit']>required_weight:
                return weight_slab