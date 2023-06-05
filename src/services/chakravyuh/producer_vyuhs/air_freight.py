from micro_services.client import common
from fastapi.encoders import jsonable_encoder
class AirFreightVyuh():
    def __init__(self, rate:dict={}):
        self.rate = rate

    def get_rate_combinations_to_extend(self):
        HANDLING_TYPES = ['stackable','non_stackable']
        PACKING_TYPES = ["pallet", "box", "crate", "loose"]
        OPERATION_TYPES = ["passenger","freighter"]
        extended_rates = []

        rate = self.rate
        factor = 2
        for handling_type in HANDLING_TYPES:
            for packing_type in PACKING_TYPES:
                for operation_type in OPERATION_TYPES:
                    rate['handling_type'] = handling_type
                    rate['packing_type'] = packing_type
                    rate['operation_type'] = operation_type
                    rate['weight_slabs'] = self.get_weight_slabs(rate["weight_slabs"],factor)
                    extended_rates.append(jsonable_encoder(rate))
        
        return extended_rates

    def extend_rate(self):
        from celery_worker import create_air_freight_rate_delay

        rates_to_create = self.get_rate_combinations_to_extend()
        #queue need to change to air_freight_rate
        for rate_to_create in rates_to_create:
            create_air_freight_rate_delay.apply_async(kwargs={ 'request':rate_to_create }, queue='fcl_freight_rate')

        return True

    def get_weight_slabs(self,weight_slabs,factor):

        new_weight_slabs = []

        for weight_slab in weight_slabs:
            weight_slab['tariff_price'] = weight_slab['tariff_price']*factor
            new_weight_slabs.append(weight_slab)
        
        return new_weight_slabs
