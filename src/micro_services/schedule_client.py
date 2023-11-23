from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url
from configs.env import APP_ENV
import json
class ScheduleApiClient:
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('sailing_schedule')),headers={
            "Authorization": "Bearer: " + RUBY_AUTHTOKEN,
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationScopeId": RUBY_AUTHSCOPEID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def get_sailing_schedule_port_pair_coverages(self, data={}):
        data['is_authorization_required'] = False
        return self.client.request('GET','get_sailing_schedule_port_pair_coverages', data)

    def get_sailing_schedule_port_pair_serviceability(self, data={}):
        data['is_authorization_required'] = False
        return self.client.request('GET','get_sailing_schedule_port_pair_serviceability', data)

    def create_sailing_schedule_port_pair_coverage(self, data={}):
        data['is_authorization_required'] = False
        return self.client.request('POST','create_sailing_schedule_port_pair_coverage', data)

    def get_sailing_schedules(self, data= {}):
        data['is_authorization_required'] = False
        if 'filters' in data:
            data['filters'] = json.dumps(data['filters'])
        return self.client.request('GET', 'get_sailing_schedules', data, timeout=3000)

    def get_fake_sailing_schedules(self, data= {}):
        data['is_authorization_required'] = False
        if 'filters' in data:
            data['filters'] = json.dumps(data['filters'])
        return self.client.request('GET', 'get_fake_sailing_schedules', data)

    def get_predicted_transit_time(self, data= {}):
        data['is_authorization_required'] = False
        if 'filters' in data:
            data['filters'] = json.dumps(data['filters'])
        return self.client.request('GET', 'get_predicted_transit_time', data)