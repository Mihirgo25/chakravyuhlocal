from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url
from configs.env import APP_ENV
import json
class MapsApiClient:
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('location')),headers={
            "Authorization": "Bearer: " + RUBY_AUTHTOKEN,
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationScopeId": RUBY_AUTHSCOPEID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def list_locations(self, data={}):
        if APP_ENV == "production":
            keys = ['filters', 'includes']
            for key in keys:
                if key in data:
                    data[key] = json.dumps(data[key])
            from configs.env import RUBY_ADDRESS_URL
            self.client.url.set('https://api.cogoport.com/location')
            res= self.client.request('GET', 'list_locations', {}, data)
            self.client.url.set(RUBY_ADDRESS_URL)
            return res
        return self.client.request('GET', 'list_locations', data, {})

    def list_location_cluster(self,data={}):
        if APP_ENV == "production":
            if 'filters' in data:
                data['filters'] = json.dumps(data['filters'])
            return self.client.request('GET','list_location_clusters',{}, data)
        return self.client.request('GET', 'list_location_clusters', data, {})

    def get_location_cluster(self,data={}):
        return self.client.request('GET','get_location_cluster',{}, data)

    def list_locations_mapping(self, data = {}):
        if APP_ENV == "production":
            return self.client.request('GET','list_locations_mapping',{}, data)
        return self.client.request('GET','list_locations_mapping',{}, data)

    def get_sea_route(self, data = {}):
        return self.client.request('GET','get_sea_route',{}, data)

    def get_service_lane(self, data= {}):
        return self.client.request('GET','get_sea_route',{}, data)

    def get_distance_matrix_valhalla(self, data= {}):
        data['is_authorization_required'] = False
        return self.client.request('GET','get_distance_matrix_valhalla',{}, data)
 
    def get_land_route_from_valhalla(self,data = {}):
        data['is_authorization_required'] = False
        data = json.dumps(data)
        return self.client.request('GET','get_land_route_location_details',data)

    def get_land_route_location_details(self,data = {}):
        from configs.env import RUBY_ADDRESS_URL
        self.client.url.set('http://10.10.11.244:8000/location')
        res=  self.client.request('GET','get_land_route_location_details',data)
        self.client.url.set(RUBY_ADDRESS_URL)
        return res
