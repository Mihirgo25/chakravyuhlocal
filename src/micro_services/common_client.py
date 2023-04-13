from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url

class CommonApiClient:
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('common')),headers={
            "Authorization": "Bearer: " + RUBY_AUTHTOKEN,
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationScopeId": RUBY_AUTHSCOPEID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def list_operators(self,data={}):
        return self.client.request('GET','list_operators',data)

    def get_money_exchange_for_fcl(self, data = {}):
        return self.client.request('GET','get_money_exchange_for_fcl', data)

    def create_communication(self, data = {}):
        return self.client.request('POST','communication/create_communication',data)

    def fcl_freight_rates_to_cogo_assured(self,data={}):
        return self.client.request('POST','update_fcl_rates_to_cogo_assured',data)
    
    def update_contract_service_task(self, data={}):
        return self.client.request('POST', 'update_contract_service_task', data)
