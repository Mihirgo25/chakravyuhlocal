from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url

class SpotSearchApiClient:
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('spot_search')),headers={
            "Authorization": "Bearer: " + 'a1e269a8-1058-4d51-9b41-9c169ab8d493',
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationScopeId": 'f3297aef-dfc1-442a-adcd-eaf9d701d558',
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def get_spot_search(self, data = {}):
        return self.client.request('GET', 'get_spot_search', data)
    
    def list_spot_searches(self, data = {}):
        return self.client.request('GET', 'list_spot_searches', data)

