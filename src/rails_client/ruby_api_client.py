from configs.env import RUBY_ADDRESS_URL
from rails_client.ruby_client import RubyClient

class RubyApiClient:
    def __init__(self):
        self.client=RubyClient(str(RUBY_ADDRESS_URL))

    def list_locations(self,data={}):
        return self.client.request('GET','list_locations',data)

    def get_eligible_service_organizations(self, data = {}):
        return self.client.request('GET','get_eligible_service_organizations',data)

    def list_operators(self,data={}):
        return self.client.request('GET','list_operators',data)

    def get_organization(self, data = {}):
        return self.client.request('GET','get_organization',data)

    def list_organizations(self, data = {}):
        return self.client.request('GET', 'list_organizations', data)

    def list_users(self, data = {}):
        return self.client.request('GET', 'list_users', data)

    def list_spot_searches(self, data = {}):
        return self.client.request('GET', 'list_spot_searches', data)

    def list_checkouts(self, data = {}):
        return self.client.request('GET', 'list_checkouts', data)

    def get_fcl_weight_slabs_configuration(self, data = {}):
        return self.client.request('GET', 'get_fcl_weight_slabs_configuration', data)

    def get_fcl_freight_local_rate_cards(self, data = {}):
        return self.client.request('GET','get_fcl_freight_local_rate_cards', data)

    def get_money_exchange_for_fcl(self, data = {}):
        return self.client.request('GET','get_money_exchange_for_fcl',data)

    def get_multiple_service_objects_data_for_fcl(self, data = {}):
        return self.client.request('GET','get_multiple_service_objects_data_for_fcl', data)

    def get_eligible_fcl_freight_rate_free_day(self, data = {}):
        return self.client.request('GET','get_eligible_fcl_freight_rate_free_day',data)

    def create_communication(self, data = {}):
        return self.client.request('POST','create_communication',data)
