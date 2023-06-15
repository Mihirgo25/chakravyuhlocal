
from configs.fcl_freight_rate_constants import EXTENSION_ENABLED_MODES, DEFAULT_SERVICE_PROVIDER_ID
from datetime import datetime, timedelta
from configs.global_constants import DEAFULT_RATE_PRODUCER_METHOD
from micro_services.client import common
from fastapi.encoders import jsonable_encoder
from configs.env import DEFAULT_USER_ID
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

class FclFreightVyuh():
    '''
        Rate Producer class to extend rates to nearby clusters and combination of rates

        It Takes 3 sources into account for rate extensions
            a. Existing Extension Rule Sets

            b. Clusters Created by Cogo Envision using predections

            c. Service lanes from CogoMaps
    '''
    
    def __init__(self, rate):
        self.rate = rate
        self.validity_start = rate['validity_start']
        self.validity_end = rate['validity_end']
        self.line_items = rate['line_items']
    
    def get_prices_sum(self, line_items, target_currency='USD'):
        total_price = 0
        for line_item in line_items:
            if line_item['currency'] != target_currency:
                total_price = total_price + common.get_money_exchange_for_fcl({"price": line_item['price'], "from_currency": line_item['currency'], "to_currency":target_currency })['price']
            else:
                total_price = total_price + line_item['price']
        return total_price
    
    def get_rate_combinations_to_extend(self):
        from services.fcl_freight_rate.helpers.fcl_freight_rate_cluster_helpers import get_fcl_freight_cluster_objects
        from services.chakravyuh.interaction.get_fcl_freight_relevant_vessel_extensions import get_fcl_freight_relevant_vessel_extensions
        from services.envision.interaction.get_fcl_freight_relevant_envision_extensions import get_fcl_freight_relevant_envision_extensions

        extension_rule_set_rates = get_fcl_freight_cluster_objects(self.rate)

        service_lane_rates = []
        # if self.rate['vessel_number']:
        #     service_lane_rates = get_fcl_freight_relevant_vessel_extensions()

        envision_cluster_rates = []
        # envision_cluster_rates = get_fcl_freight_relevant_envision_extensions()

        return extension_rule_set_rates + service_lane_rates + envision_cluster_rates
    
    def get_existing_system_rates(self, requirement):
        from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
        next_two_days = (datetime.now() - timedelta(days=2)).date()
        existing_system_rates_query = FclFreightRate.select(
            FclFreightRate.id,
            FclFreightRate.mode,
            FclFreightRate.validities,
            FclFreightRate.service_provider_id,
            FclFreightRate.shipping_line_id,
            FclFreightRate.cogo_entity_id
        ).where(
            FclFreightRate.origin_port_id == requirement["origin_poirt_id"],
            FclFreightRate.destination_port_id == requirement['destination_port_id'],
            FclFreightRate.container_type == requirement['container_type'],
            FclFreightRate.container_size == requirement['container_size'],
            FclFreightRate.commodity == requirement['commodity'],
            FclFreightRate.mode != 'predicted',
            FclFreightRate.rate_type == DEFAULT_RATE_TYPE,
            FclFreightRate.importer_exporter_id.is_null(True),
            FclFreightRate.last_rate_available_date > next_two_days,
           ~FclFreightRate.rate_not_available_entry
        )
        existing_system_rates = jsonable_encoder(list(existing_system_rates_query.dicts()))
        return existing_system_rates
    
    def get_validities_to_create_for_minimum(self, current_rate_price, rate_validity, to_add_validity_start, to_add_validity_end):
        validities_to_create = []
        line_items = rate_validity['line_items']
        current_validity_price = self.get_prices_sum(line_items, 'USD')
        validity_start = datetime.fromisoformat(rate_validity['validity_start']).date()
        validity_end = datetime.fromisoformat(rate_validity['validity_end']).date()
        if current_rate_price > current_validity_price:
            if (to_add_validity_start < validity_start and to_add_validity_end < validity_start) or (to_add_validity_start > validity_end and to_add_validity_end > validity_end):
                """
                Case 1: No overlap
                  ---------- 
                              -----------
                            OR
                              -----------
                  ----------
                """
                validities_to_create.append({
                    'validity_start': to_add_validity_start,
                    'validity_end': to_add_validity_end
                })
            if validity_start > to_add_validity_start and validity_end < to_add_validity_end:
                """
                Case 2: 
                Current Validity :     -------------
                New Validity     :  ---------------------
                """
                start_validity = {
                    'validity_start': to_add_validity_start,
                    'validity_end': validity_start
                }
                end_validity = {
                    'validity_start': validity_end,
                    'validity_end': to_add_validity_end
                }
                validities_to_create =  validities_to_create + [start_validity, end_validity]
            elif validity_start > to_add_validity_start and validity_end > to_add_validity_end:
                """
                Case 3: 
                Current Validity :     -------------
                New Validity     :  ---------
                """
                validities_to_create.append(                                    {
                    'validity_start': to_add_validity_start,
                    'validity_end': validity_start
                    })
            elif validity_end > to_add_validity_start and validity_end < to_add_validity_end:
                """
                Case 4: 
                Current Validity :     -------------
                New Validity     :           ---------------
                """
                validities_to_create.append({
                    'validity_start': validity_end,
                    'validity_end': to_add_validity_end
                })

            elif current_rate_price < current_validity_price: # Always overide with new price of its smaller
                validities_to_create.append({
                    'validity_start': to_add_validity_start,
                    'validity_end': to_add_validity_end
                })
        return validities_to_create
    
    def get_validities_to_create_for_maximum(self, current_rate_price, rate_validity, to_add_validity_start, to_add_validity_end):
        validities_to_create = []
        line_items = rate_validity['line_items']
        current_validity_price = self.get_prices_sum(line_items, 'USD')
        validity_start = datetime.fromisoformat(rate_validity['validity_start']).date()
        validity_end = datetime.fromisoformat(rate_validity['validity_end']).date()
        if current_rate_price < current_validity_price: # Check conditions when new price is lower
            if (to_add_validity_start < validity_start and to_add_validity_end < validity_start) or (to_add_validity_start > validity_end and to_add_validity_end > validity_end):
                '''
                Case 1: No overlap
                  ---------- 
                              -----------
                            OR
                              -----------
                  ----------
                '''
                validities_to_create.append({
                    'validity_start': to_add_validity_start,
                    'validity_end': to_add_validity_end
                })
            elif validity_start > to_add_validity_start and validity_end < to_add_validity_end:
                """
                Case 2: 
                Current Validity :     -------------
                New Validity     :  ---------------------
                """
                start_validity = {
                    'validity_start': to_add_validity_start,                                    
                    'validity_end': validity_start
                }
                end_validity = {
                    'validity_start': validity_end,
                    'validity_end': to_add_validity_end
                }
                validities_to_create =  validities_to_create + [start_validity, end_validity]
            
            elif validity_start > to_add_validity_start and validity_end > to_add_validity_end:
                """
                Case 3: 
                Current Validity :     -------------
                New Validity     :  ---------
                """
                validities_to_create.append(
                    {
                    'validity_start': to_add_validity_start,
                    'validity_end': validity_start
                    }
                )
            elif validity_end > to_add_validity_start and validity_end < to_add_validity_end:
                """
                Case 4: 
                Current Validity :     -------------
                New Validity     :           ---------------
                """
                validities_to_create.append({
                    'validity_start': validity_end,
                    'validity_end': to_add_validity_end
                })
            
        elif current_rate_price > current_validity_price: # Always overide with new price of its greater
            validities_to_create.append({
                'validity_start': to_add_validity_start,
                'validity_end': to_add_validity_end
            })

        return validities_to_create

    
    def get_eligible_validities_to_create(self, requirement):

        existing_system_rates = self.get_existing_system_rates(requirement)

        to_add_validity_start = self.validity_start
        to_add_validity_end = self.validity_end

        if len(existing_system_rates) == 0:
            # Add full validity if no rate is available
            return to_add_validity_start, to_add_validity_end
        

        current_rate_price = self.get_prices_sum(self.line_items, 'USD')

        cogo_freight_rates_for_current_sl = []

        validities_to_create = []

        for esr in existing_system_rates:
            rate_validities = esr['validities'] or []
            if rate_validities and esr['service_provider_id'] == DEFAULT_SERVICE_PROVIDER_ID and esr['shipping_line_id'] == requirement['shipping_line_id'] and not esr['cogo_entity_id']:
                cogo_freight_rates_for_current_sl.append(esr)

                for rate_validity in rate_validities:
                    if DEAFULT_RATE_PRODUCER_METHOD == 'minimum':
                        validities_to_create = self.get_validities_to_create_for_minimum(
                            current_rate_price,
                            rate_validity,
                            to_add_validity_start,
                            to_add_validity_end
                        )
                    if DEAFULT_RATE_PRODUCER_METHOD == 'maximum':
                        validities_to_create = self.get_validities_to_create_for_maximum(
                            current_rate_price,
                            rate_validity,
                            to_add_validity_start,
                            to_add_validity_end
                        )

                break # There will always be a single rate matching this combination
        return validities_to_create
    
    def create_fcl_freight_rate(self, rate_to_create):
        '''
            Creates rates for single combination of rate extension
        '''
        from celery_worker import create_fcl_freight_rate_delay
        validity_start = self.validity_start
        validity_end = self.validity_end
        validities_to_create = [{ 'validity_start': validity_start, 'validity_end': validity_end }]

        if DEAFULT_RATE_PRODUCER_METHOD != 'latest':
            validities_to_create = self.get_eligible_validities_to_create(rate_to_create)
        
        for validity in validities_to_create:
            freight_rate_object = rate_to_create | validity | { 'mode': 'rate_extension', 'service_provider_id': DEFAULT_SERVICE_PROVIDER_ID, "sourced_by_id": DEFAULT_USER_ID, "procured_by_id": DEFAULT_USER_ID, "performed_by_id": DEFAULT_USER_ID }

            create_fcl_freight_rate_delay.apply_async(kwargs={ 'request':freight_rate_object }, queue='fcl_freight_rate')
            
        return True
    


    def extend_rate(self):
        '''
            Rate producer function to extend rates to nearby clusters and combination of rates
        '''
        if self.rate['mode'] not in EXTENSION_ENABLED_MODES:
            return True

        rates_to_create = self.get_rate_combinations_to_extend()

        for rate_to_create in rates_to_create:
            self.create_fcl_freight_rate(rate_to_create | {'extended_from_id' : self.rate['id']})

        return True