from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url

class AuthApiClient:
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('organization')),headers={
            "Authorization": "Bearer: " + RUBY_AUTHTOKEN,
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationScopeId": RUBY_AUTHSCOPEID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
        
    def update_organization(self,data={}):
        return self.client.request('POST','update_organization',data)

    def list_organization_services(self, data):
        return self.client.request('GET','list_organization_services', data)  

    def create_organization_serviceable_port(self, data):
        return self.client.request('POST', 'create_organization_serviceable_port', data)