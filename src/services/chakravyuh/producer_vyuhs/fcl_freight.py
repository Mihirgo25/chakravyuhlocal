
from configs.fcl_freight_rate_constants import EXTENSION_ENABLED_MODES
class FclFreightVyuh():
    def __init__(self, rate):
        self.rate = rate
    
    def get_missing_or_outdated_rates(self):
        from services.fcl_freight_rate.helpers.fcl_freight_rate_cluster_helpers import get_fcl_freight_cluster_objects
        from services.chakravyuh.interaction.get_fcl_freight_relevant_vessel_extensions import get_fcl_freight_relevant_vessel_extensions
        from services.envision.interaction.get_fcl_freight_relevant_envision_extensions import get_fcl_freight_relevant_envision_extensions

        extension_rule_set_rates = get_fcl_freight_cluster_objects(self.rate)

        service_lane_rates = []
        if self.rate['vessel_number']:
            service_lane_rates = get_fcl_freight_relevant_vessel_extensions()

        envision_cluster_rates = get_fcl_freight_relevant_envision_extensions()

        return []
    
    def build_rate_object(self, rate_to_create):
        return {
            "origin_port_id": rate_to_create["origin_port_id"]
        }
    
    def create_fcl_freight_rate(self, rate_to_create):
        from celery_worker import create_fcl_freight_rate_delay
        freight_rate_object = self.build_rate_object(rate_to_create)
        create_fcl_freight_rate_delay.apply_async(kwargs={ 'request':freight_rate_object },queue='fcl_freight_rate')
        return True


    def extend_rate(self):
        if self.rate['mode'] not in EXTENSION_ENABLED_MODES:
            return True

        rates_to_create = self.get_missing_or_outdated_rates()

        for rate_to_create in rates_to_create:
            self.create_fcl_freight_rate(rate_to_create)

        return True