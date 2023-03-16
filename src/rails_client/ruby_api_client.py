from configs.env import RUBY_ADDRESS_URL
from rails_client.ruby_client import RubyClient
import json
import requests

class RubyApiClient:
    def __init__(self):
        self.client=RubyClient(str(RUBY_ADDRESS_URL))

    # def list_locations(self,data={}):
    #     return self.client.request('GET','list_locations',data)
    

    def get_eligible_service_organizations(self, data = {}):
        return self.client.request('GET','get_eligible_service_organizations',data)

    def list_operators(self,data={}):
        return self.client.request('GET','list_operators',data)

    def list_organizations(self,data={}):
        return self.client.request('GET','list_organizations',data)

    def get_eligible_fcl_freight_rate_free_day(self, data = {}):
        return self.client.request('GET','get_eligible_fcl_freight_rate_free_day',data)
        
    def list_fcl_freight_commodity_cluster(self, data={}):
        return self.client.request('GET','list_fcl_freight_commodity_cluster',data)

    def list_spot_searches(self, data = {}):
        return self.client.request('GET', 'list_spot_searches', data)

    def list_checkouts(self, data = {}):
        return self.client.request('GET', 'list_checkouts', data)

    def list_location_cluster(self,data={}):
        return self.client.request('GET','list_location_cluster',data)

    def get_location_cluster(self, data = {}):
        return self.client.request('GET','get_location_cluster',data)
    
    def get_money_exchange_for_fcl(self, data = {}):
        return self.client.request('GET','get_money_exchange_for_fcl',data)

    def get_fcl_freight_commodity_cluster(self, data = {}):
        return self.client.request('GET','get_fcl_freight_commodity_cluster',data)
    
    def get_multiple_service_objects_data_for_fcl(self, data = {}):
        return self.client.request('GET','get_multiple_service_objects_data_for_fcl', data)

    def get_eligible_fcl_freight_rate_free_day(self, data = {}):
        return self.client.request('GET','get_eligible_fcl_freight_rate_free_day',data)

    def create_sailing_schedule_port_pair_coverage(self, data = {}):
        return self.client.request('POST','create_sailing_schedule_port_pair_coverage',data)

    def create_communication(self, data = {}):
        return self.client.request('POST','create_communication',data)
    
    def get_shipment(self, data = {}):
        return self.client.request('GET','get_shipment',data)

    
    def bulk_update_shipment_quotations(self, data = {}):
        return self.client.request('POST', 'bulk_update_shipment_quotations', data)
    
    def list_users(self, data = {}):
        return self.client.request('GET', 'list_users', data)
    
    def get_platform_config_constant(self, data = {}):
        return self.client.request('GET','get_platform_config_constant',data)
    def list_fcl_freight_rate_free_days(self, data = {}):
        return self.client.request('GET', 'list_fcl_freight_rate_free_days', data)
    
    def get_spot_search(self, data = {}):
        return self.client.request('GET', 'get_spot_search', data)

    def list_partner_user_expertises(self, data = {}):
        return self.client.request('GET', 'list_partner_user_expertises', data)

    def get_users(self, data = {}):
        return self.client.request('GET', 'get_users', data)

    def get_fcl_freight_rates(self, data = {}):
        return self.client.request('GET','get_fcl_freight_rates', data)
    
    def list_organization_services(self, data = {}):
        return self.client.request('GET','list_organization_services', data)
    
    def get_organization(self, data = {}):
        return self.client.request('GET', 'get_organization', data)
    
    
    def update_organization(self,data={}):
        return self.client.request('POST','update_organization',data)