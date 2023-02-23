from configs.env import RUBY_ADDRESS_URL
from rails_client.ruby_client import RubyClient

class RubyApiClient:
    def __init__(self):
        self.client=RubyClient(str(RUBY_ADDRESS_URL))

    def list_locations(self,data={}):
        return self.client.request('GET','list_locations',data)

    def list_operators(self,data={}):
        return self.client.request('GET','list_operators',data)

    def list_organizations(self,data={}):
        return self.client.request('GET','list_organizations',data)

    def list_fcl_freight_commodity_cluster(self, data={}):
        return self.client.request('GET','list_fcl_freight_commodity_cluster',data)

    def list_location_cluster(self,data={}):
        return self.client.request('GET','list_location_cluster',data)

    def get_location_cluster(self, data = {}):
        return self.client.request('GET','get_location_cluster',data)
    
    def get_money_exchange_for_fcl(self, data = {}):
        return self.client.request('GET','get_money_exchange_for_fcl',data)

    def get_fcl_freight_commodity_cluster(self, data = {}):
        return self.client.request('GET','get_fcl_freight_commodity_cluster',data)
    
    def get_multiple_service_objects_data_for_fcl(self, data = {}):
        return self.client.request('GET','get_multiple_service_objects_data_for_fcl',data)