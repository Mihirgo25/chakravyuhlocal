from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url

class PartnerApiClient:
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('partner')),headers={
            "Authorization": "Bearer: " + RUBY_AUTHTOKEN,
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationScopeId": RUBY_AUTHSCOPEID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
    
    def list_partner_users(self, data):
        return self.client.request('GET', 'list_partner_users', data)
    
    def list_partner_user_expertises(self, data):
        return self.client.request('GET', 'list_partner_user_expertises', data)