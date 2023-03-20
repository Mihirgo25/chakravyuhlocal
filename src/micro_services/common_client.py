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

    def list_partners(self, data):
        return self.client.request('GET', 'list_partners', data)
    
    def create_sailing_schedule_port_pair_coverage(self, data = {}):
        return self.client.request('POST','create_sailing_schedule_port_pair_coverage',data)
        
    def get_money_exchange_for_fcl(self, data = {}):
        return self.client.request('GET','get_money_exchange_for_fcl', data)

    def list_spot_searches(self, data = {}):
        return self.client.request('GET', 'list_spot_searches', data)
    
    def list_checkouts(self, data = {}):
        return self.client.request('GET', 'list_checkouts', data)
    
    def get_spot_search(self, data = {}):
        return self.client.request('GET', 'get_spot_search', data)
    
    def create_communication(self, data = {}):
        return self.client.request('POST','create_communication',data)
    
    def bulk_update_shipment_quotations(self, data = {}):
        return self.client.request('GET','bulk_update_shipment_quotations',data)
    
    def get_shipment(self, data = {}):
        return self.client.request('GET','get_shipment',data)