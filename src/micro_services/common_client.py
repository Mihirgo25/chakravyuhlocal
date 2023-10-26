from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url
from rms_utils.get_money_exchange_for_fcl_fallback import get_money_exchange_for_fcl_fallback
from rms_utils.list_exchange_currencies_fallback import list_exchange_currencies_fallback
from libs.cached_money_exchange import get_money_exchange_from_rd, set_money_exchange_to_rd
from libs.get_saas_schedules_airport_pair_coverages_from_rd import get_saas_schedules_airport_pair_coverages_from_rd, set_saas_schedules_airport_pair_coverages_to_rd
from libs.get_exhange_currencies_from_rd import list_exchange_rate_currencies_from_rd,set_exchange_rate_currencies_to_rd
from configs.yml_definitions import FCL_FREIGHT_CURRENCIES
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
    
    def list_exchange_rate_currencies(self):
        cached_resp = list_exchange_rate_currencies_from_rd()
        if cached_resp:
            return cached_resp

        resp = self.client.request('GET', 'list_exchange_rate_currencies', timeout=5, data={"page_limit": 200})

        if isinstance(resp, dict) and resp.get('list'):
            currency_code = [entry['iso_code'] for entry in resp.get('list', [])]
            set_exchange_rate_currencies_to_rd(currency_code)
            return currency_code
        
        return FCL_FREIGHT_CURRENCIES
    
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
    
    def create_saas_air_schedule_airport_pair_coverage(self,data={}):
        return self.client.request('POST','create_saas_air_schedule_airport_pair_coverage',data)

    def get_saas_schedules_airport_pair_coverages(self,data={}):
        cached_resp = get_saas_schedules_airport_pair_coverages_from_rd(data)
        if cached_resp:
            return cached_resp
        
        resp = self.client.request('GET','get_saas_schedules_airport_pair_coverages',data)
        if isinstance(resp,list):
            set_saas_schedules_airport_pair_coverages_to_rd(data.get('origin_airport_id'), data.get('destination_airport_id'), resp)
            return resp
        return resp

    def update_spot_negotiation_locals_rate(self,data = {}):
        return self.client.request('POST','spot_negotiation/update_spot_negotiation_locals_rate',data)
    
    def get_exchange_rate(self, data = {}):
        return self.client.request('GET', 'get_exchange_rate', data)     
    
    def get_all_exchange_rates(self, data = {}):
        return self.client.request('GET','get_all_exchange_rates',data)

    def list_chat_agents(self, data = {}):
        return self.client.request('GET','communication/list_chat_agents',data)
    
    
    
    
    