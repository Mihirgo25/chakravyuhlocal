from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID
from configs.global_constants import DEFAULT_SERVICE_PROVIDER_ID
from configs.transformation_constants import HANDLING_TYPE_FACTORS, PACKING_TYPE_FACTORS, OPERATION_TYPE_FACTORS
class AirFreightVyuh():
    def __init__(self, rate:dict={}):
        self.rate = rate

    def get_rate_combinations_to_extend(self):
        HANDLING_TYPES = ['stackable','non_stackable']
        PACKING_TYPES = ["pallet", "box", "crate", "loose"]
        OPERATION_TYPES = ["passenger","freighter"]
        extended_rates = []

        for handling_type in HANDLING_TYPES:
            for packing_type in PACKING_TYPES:
                for operation_type in OPERATION_TYPES:
                    rate = jsonable_encoder(self.rate)
                    rate['handling_type'] = handling_type
                    rate['packing_type'] = packing_type
                    rate['operation_type'] = operation_type
                    rate['weight_slabs'] = self.get_weight_slabs(rate)
                    extended_rates.append(rate)
        
        return extended_rates

    def extend_rate(self):
        from celery_worker import create_air_freight_rate_delay

        rates_to_create = self.get_rate_combinations_to_extend()

        # queue need to change to air_freight_rate
        for rate_to_create in rates_to_create:
            rate_to_create = rate_to_create | { 'mode': 'rate_extension', 'service_provider_id': DEFAULT_SERVICE_PROVIDER_ID, "sourced_by_id": DEFAULT_USER_ID, "procured_by_id": DEFAULT_USER_ID, "performed_by_id": DEFAULT_USER_ID }
            create_air_freight_rate_delay.apply_async(kwargs={ 'request':rate_to_create }, queue='fcl_freight_rate')

        return True

    def get_weight_slabs(self,rate):

        weight_slabs = rate['weight_slabs']

        original_rate_handling_type = self.rate['stacking_type']
        original_rate_packing_type = self.rate['shipment_type']
        original_rate_operation_type = self.rate['operation_type']

        current_rate_handling_type = rate['stacking_type']
        current_rate_packing_type = rate['shipment_type']
        current_rate_operation_type = rate['operation_type']

        handling_type_factor = (HANDLING_TYPE_FACTORS[current_rate_handling_type] or 1) / (HANDLING_TYPE_FACTORS[original_rate_handling_type] or 1)
        packing_type_factor = (PACKING_TYPE_FACTORS[current_rate_packing_type] or 1) / (PACKING_TYPE_FACTORS[original_rate_packing_type] or 1)
        operation_type_factor = (OPERATION_TYPE_FACTORS[current_rate_operation_type] or 1) / (OPERATION_TYPE_FACTORS[original_rate_operation_type] or 1)

        new_weight_slabs = []
        for weight_slab in weight_slabs:
            new_weight_slab = jsonable_encoder(weight_slab)
            new_weight_slab['tariff_price'] = weight_slab['tariff_price'] * handling_type_factor * packing_type_factor * operation_type_factor
            new_weight_slabs.append(new_weight_slab)
        
        return new_weight_slabs
