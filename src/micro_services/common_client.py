from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url
from rms_utils.get_money_exchange_for_fcl_fallback import get_money_exchange_for_fcl_fallback
from libs.cached_money_exchange import get_money_exchange_from_rd, set_money_exchange_to_rd

class CommonApiClient:
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('common')),headers={
            "Authorization": "Bearer: " + RUBY_AUTHTOKEN,
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationParameters": ":allowed",
            # "AuthorizationScopeId": RUBY_AUTHSCOPEID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def get_money_exchange_for_fcl(self, data = {}):

        cached_resp = get_money_exchange_from_rd(data)
        if cached_resp:
            return { "price": cached_resp }
        
        resp = self.client.request('GET','get_money_exchange_for_fcl', data,timeout = 5)
        if isinstance(resp,dict) and resp.get('price') is not None:
            conversion_rate = resp.get('rate') or resp['price']/float(data['price'])
            
            set_money_exchange_to_rd(data.get('from_currency'), data.get('to_currency'), conversion_rate)
            return resp
        
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
    
    def list_revenue_desk_show_rates(self,data = {}):
        return self.client.request('GET','list_revenue_desk_show_rates',data)
    
    def update_spot_negotiation_locals_rate(self,data = {}):
        return self.client.request('POST','spot_negotiation/update_spot_negotiation_locals_rate',data)
    
    def get_exchange_rate(self, data = {}):
        return self.client.request('GET', 'get_exchange_rate', data)     
    
    def get_all_exchange_rates(self, data = {}):
        return self.client.request('GET','get_all_exchange_rates',data)

    
    # def get_sailing_schedules(self, data= {}):
    #     return self.client.request('GET', 'sailing_schedule/get_sailing_schedules', data, timeout=15000)

    # def get_fake_sailing_schedules(self, data= {}):
    #     return self.client.request('GET', 'sailing_schedule/get_fake_sailing_schedules', data)

    # def get_predicted_transit_time(self, data= {}):
    #     return self.client.request('GET', 'sailing_schedule/get_predicted_transit_time', data)

    