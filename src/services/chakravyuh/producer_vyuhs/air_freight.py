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

        for handling_type in HANDLING_TYPES:
            for packing_type in PACKING_TYPES:
                for operation_type in OPERATION_TYPES:
                    self.rate['handling_type'] = handling_type
                    self.rate['packing_type'] = packing_type
                    self.rate['operation_type'] = operation_type
                    
                    extended_rates.append(jsonable_encoder(self.rate))
        
        return extended_rates

    def create_air_freight_rate(self):
        return common.create_air_freight_rate(self.rate)

    def extend_rate(self):
        rates_to_create = self.get_rate_combinations_to_extend()

        for rate_to_create in rates_to_create:
            self.create_air_freight_rate(rate_to_create)

        return True

