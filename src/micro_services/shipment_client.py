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

    def list_shipment_collection_party(self,data={}):
        return self.client.request('GET','list_shipment_collection_party',data)
    
    def get_shipment_services_quotation(self,data={}):
        return self.client.request('GET','get_shipment_services_quotation',data)
    
    def update_shipment_buy_quotations(self,data={}):
        return self.client.request('POST','update_shipment_buy_quotations',data)
    
    def list_shipments(self,data = {}):
        return self.client.request('GET','list_shipments',data)
    
    def list_shipment_sell_quotations(self,data={}):
        return self.client.request('GET','list_shipment_sell_quotation_for_chakravyuh',data)
    
    def get_shipment_sell_and_buy_quotation(self,data={}):
        return self.client.request('GET','get_shipment_sell_and_buy_quotation',data)
    
    def get_new_sell_data(self,data={}):
        return self.client.request('GET','get_new_sell_data',data)
    
    def get_shipment_quotation(self,data={}):
        return self.client.request('GET','get_shipment_quotation',data)