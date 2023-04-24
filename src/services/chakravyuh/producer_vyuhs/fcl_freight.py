
class FclFreightVyuh():
    def __init__(self, rate):
        self.rate = rate
    
    def get_missing_or_outdated_rates(self):
        
        return []

    def get_single_rate_delta(self, rate):
        return { "code": "BAS", "unit": "per_container", "price": 0, "currency": "USD" }
    
    def get_delta_for_all_missing_rates(self, to_create_rates):
        for missing_rate in to_create_rates:
            missing_rate['delta'] = self.get_single_rate_delta(missing_rate)
    
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
        rates_to_create = self.get_missing_or_outdated_rates()
        rates_to_create_with_delta = self.get_delta_for_all_missing_rates(rates_to_create)

        for rate_to_create in rates_to_create_with_delta:
            self.create_fcl_freight_rate(rate_to_create)

        return True