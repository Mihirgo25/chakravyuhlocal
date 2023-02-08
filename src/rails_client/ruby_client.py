import requests
from configs.env import *
import json

class RubyClient:

    url_path = '/'

    def __init__(self,url):
        self.url = url
        self.status_code = None
        self.headers = {
            'Authorization': 'Bearer: ' + RUBY_AUTHTOKEN,
            'AuthorizationScope': RUBY_AUTHSCOPE,
            'AuthorizationScopeId': RUBY_AUTHSCOPEID,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def request(self, method, action, params={}):

        kwargs = {
            'url': self.normalize_url(action),
            'headers': self.headers,
            'data': json.dumps(params)
        }

        response = requests.request(method, **kwargs)

        data = response.content

        if not data:
            return {"message": "no response"}
        
        try:
            result=json.loads(response.text)
        except:
            print(data)
            return {"message": "no response"}

        return result

    def normalize_url(self, action):
        return self.url + self.url_path + action
