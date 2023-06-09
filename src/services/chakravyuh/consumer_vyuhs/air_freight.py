from services.chakravyuh.models.air_freight_rate_estimation import AirFreightRateEstimation
from fastapi.encoders import jsonable_encoder
from micro_services.client import common

class AirFreightVyuh():
    def __init__(self, freight_rates: list = [],requirements: dict = {},weight: float = 0.0):
        self.freight_rates = freight_rates
        self.requirements = requirements
        self.weight = weight

    def get_probable_rate_transformations(self):
        origin_location_ids = [self.requirements['origin_country_id']]
        destination_location_ids = [self.requirements['destination_country_id']]

        airline_ids = []

        for freight_rate in self.freight_rates:
            airline_ids.append(freight_rate['airline_id'])

        transformation_query = AirFreightRateEstimation.select().where(
            AirFreightRateEstimation.origin_location_id << origin_location_ids,
            AirFreightRateEstimation.destination_location_id << destination_location_ids,
            AirFreightRateEstimation.operation_type == self.requirements['operation_type'],
            AirFreightRateEstimation.commodity == self.requirements['commodity'],
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
    
    def get_modified_weight_slab(self,estimation_weight_slab,rate):

        avg_price = estimation_weight_slab['avg_price']
        for rate in rate['freights']:
            for line_item in rate['line_items']:
                if line_item['code'] == 'BAS':
                    line_item['price'] = avg_price
        return rate


    def get_weight_slab(self,estimation_weight_slabs,rate):
        found = False
        for estimation_weight_slab in estimation_weight_slabs:
            if self.weight >= estimation_weight_slab['lower_limit'] and self.weight <= estimation_weight_slab['upper_limit']:
                rate = self.get_modified_weight_slab(estimation_weight_slab,rate)
                found = True
                break
        if not found:
            estimation_weight_slab = estimation_weight_slabs[0]
            rate = self.get_modified_weight_slab(estimation_weight_slab,rate)
        return rate
    

    def apply_rate_transformation(self, rate, probable_transformations):
        probable_transformation_to_apply = self.get_most_eligible_rate_transformation(probable_transformations)
        rate = self.get_weight_slab(probable_transformation_to_apply.get('weight_slabs'),rate)
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

        return new_rate

    def apply_dynamic_pricing(self):
        self.set_requirements(self.freight_rates[0])

        probable_transformations = self.get_probable_rate_transformations()
 
        if len(probable_transformations)==0:
            return self.freight_rates

        probable_customer_transformations = self.get_probable_customer_transformations()

        new_freight_rates = []
        for freight_rate in self.freight_rates:
            new_freight_rate = self.apply_transformation(
                    rate = freight_rate,
                    probable_transformations=probable_transformations,
                    probable_customer_transformations=probable_customer_transformations,
                )
            
            new_freight_rates.append(new_freight_rate)
        
        return new_freight_rates
    
    def set_requirements(self,freight_rate):
        self.requirements ={

                'origin_airport_id':freight_rate['origin_airport_id'],
                'destination_airport_id':freight_rate['destination_airport_id'],
                'origin_country_id':freight_rate['origin_country_id'],
                'destination_country_id':freight_rate['destination_country_id'],
                'commodity':freight_rate['commodity'],
                'airline_id':freight_rate['airline_id'],
                'operation_type':freight_rate['operation_type'],
                'stacking_type':freight_rate['stacking_type'],
                'shipment_type':freight_rate['shipment_type']
                }
    
    