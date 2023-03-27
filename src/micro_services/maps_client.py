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

    def list_locations(self, data):
        if APP_ENV == "production":
            if 'filters' in data:
                data['filters'] = json.dumps(data['filters'])
        return self.client.request('GET', 'list_locations', data)

    def list_location_cluster(self,data={}):
        return self.client.request('GET','list_location_clusters',data)

    def get_location_cluster(self,data={}):
        return self.client.request('GET','get_location_cluster',data)
