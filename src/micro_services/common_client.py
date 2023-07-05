from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url
from rms_utils.get_money_exchange_for_fcl_fallback import get_money_exchange_for_fcl_fallback

class CommonApiClient:
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('common')),headers={
            "Authorization": "Bearer: " + RUBY_AUTHTOKEN,
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationScopeId": RUBY_AUTHSCOPEID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def get_money_exchange_for_fcl(self, data = {}):
        resp = self.client.request('GET','get_money_exchange_for_fcl', data,timeout = 5)
        if isinstance(resp,dict) and resp.get('status_code') and resp.get('status_code')==408:
            resp = get_money_exchange_for_fcl_fallback(**data)
        return resp

    def create_communication(self, data = {}):
        return self.client.request('POST','communication/create_communication',data, timeout=60)

    def fcl_freight_rates_to_cogo_assured(self,data={}):
        return self.client.request('POST','update_fcl_rates_to_cogo_assured',data, timeout=60)

    def update_contract_service_task(self, data={}):
        return self.client.request('POST', 'update_contract_service_task', data)
    
    def create_air_freight_rate(self, data={}):
        return self.client.request('POST', 'air_freight_rate/create_air_freight_rate', data)
    
    def create_saas_air_schedule_airport_pair(self, data={}):
        return self.client.request('POST', 'create_saas_air_schedule_airport_pair', data)
    
    def get_air_routes_and_schedules_from_cargo_ai(self,data={}):
        return self.client.request('GET','get_air_routes_and_schedules_from_cargo_ai',data)

