from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url

class ShipmentApiClient:
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('shipment')),headers={
            "Authorization": "Bearer: " + RUBY_AUTHTOKEN,
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationScopeId": RUBY_AUTHSCOPEID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def bulk_update_shipment_quotations(self, data):
        return self.client.request('POST', 'bulk_update_shipment_quotations', data)
    
    def get_shipment(self, data = {}):
        return self.client.request('GET','get_shipment',data)
    
    def list_shipments(self,data = {}):
        return self.client.request('GET','list_shipments',data)
    
    def list_shipment_sell_quotations(self,data={}):
        return self.client.request('GET','list_shipment_sell_quotations',data)
    
    def get_previous_shipment_airlines(self,data={}):
        return self.client.request('GET','get_previous_shipment_airlines',data)