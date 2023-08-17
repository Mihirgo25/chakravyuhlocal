from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url

class SpotSearchApiClient:
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('spot_search')),headers={
            "Authorization": "Bearer: " + RUBY_AUTHTOKEN,
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationScopeId": RUBY_AUTHSCOPEID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def get_spot_search(self, data = {}):
        return self.client.request('GET', 'get_spot_search', data)
    
    def list_spot_searches(self, data = {}):
        return self.client.request('GET', 'list_spot_searches', data)

    def send_spot_search_rate_update(self,data={}):
        return self.client.request('GET','send_spot_search_rate_update',data)

