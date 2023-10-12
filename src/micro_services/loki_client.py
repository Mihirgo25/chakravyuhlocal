from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url
from libs.get_charges_yml import get_charge_from_rd, set_charge_to_rd
from rms_utils.get_charge_fallback import get_charge_fallback

class LokiApiClient:
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('loki')),headers={
            "Authorization": "Bearer: " + RUBY_AUTHTOKEN,
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationScopeId": RUBY_AUTHSCOPEID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })
    
    def get_charge(self, charge_name):
        cached_resp = get_charge_from_rd(charge_name)
        if cached_resp:
            return cached_resp
        
        data = {"serviceChargeType": charge_name, "conditionLang": "PYTHON"}
        resp = self.client.request('GET', 'charge-code/list',data , timeout=5)

        if isinstance(resp,dict):
            set_charge_to_rd(charge_name, resp)
            return resp
        
        return get_charge_fallback(charge_name)
    
    def migrate_charge_codes(self, data = {}):
        return self.client.request('POST', 'migrate-python-conditions', data)