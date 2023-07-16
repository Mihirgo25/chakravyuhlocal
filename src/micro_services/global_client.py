import httpx
from configs.env import *
import json
import re
from fastapi.encoders import jsonable_encoder
from contextvars import ContextVar
import urllib

def http_build_query(data):
    parents = list()
    pairs = dict()

    def renderKey(parents):
        depth, outStr = 0, ''
        for x in parents:
            s = "[%s]" if depth > 0 or isinstance(x, int) else "%s"
            outStr += s % str(x)
            depth += 1
        return outStr

    def r_urlencode(data):
        if isinstance(data, list) or isinstance(data, tuple):
            for i in range(len(data)):
                parents.append(i)
                r_urlencode(data[i])
                parents.pop()
        elif isinstance(data, dict):
            for key, value in data.items():
                parents.append(key)
                r_urlencode(value)
                parents.pop()
        else:
            pairs[renderKey(parents)] = str(data)

        return pairs
    return urllib.parse.urlencode(r_urlencode(data))
class GlobalClient:
    def __init__(self, url,headers):
        self.client = httpx.Client()
        if APP_ENV !='production':
            self.url = ContextVar('client_base_url', default=RUBY_ADDRESS_URL)
        else:
            self.url = url
        self.headers = headers

    def request(self, method, action, data={}, params={}, timeout = 15):
            
        if isinstance(data, dict):
            data = jsonable_encoder(data)
        if isinstance(params, dict):
            params = jsonable_encoder(params)
                    
        kwargs = {
            "headers": self.headers,
            "url": self.normalize_url(action),
            "timeout": timeout,
        }
        
        if method == 'POST' and data:
            kwargs['data'] = json.dumps(data)
        elif method == 'GET':
            if data: 
                prefinal_url = str(http_build_query(data))
                final_url = re.sub(r'%5D%5B\d+%5D','%5D%5B%5D',prefinal_url)
                kwargs['url'] = kwargs['url'] + '?' + final_url  # Rails backend
            else:
                kwargs['params'] = params  # Python Backend   
        try:
            if method == 'GET':
                response = self.client.get(**kwargs)
            else:
                response = self.client.post(**kwargs)
        except httpx.TimeoutException as exc:
            return { 'status_code': 408 }

        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return f"HTTP Exception for {exc.request.url} - {exc} - {response.content}"

        try:
            return json.loads(response.content)
        except Exception as e:
            return e

    def normalize_url(self, action):
        url = self.url.get() if APP_ENV!='production' else self.url
        return url + "/" + action
