import httpx
from configs.env import *
import json
from fastapi.encoders import jsonable_encoder
from contextvars import ContextVar
class GlobalClient:
    def __init__(self, url,headers):
        self.client = httpx.Client(timeout=20.0)
        if APP_ENV !='production':
            self.url = ContextVar('client_base_url', default=RUBY_ADDRESS_URL)
        else:
            self.url = url
        self.headers = headers

    def request(self, method, action, data={}, params={},timeout = None):
        client = self.client
        
        if timeout:
            client = httpx.Client(timeout=timeout)
            
        if isinstance(data, dict):
            data = jsonable_encoder(data)
        kwargs = {
            "headers": self.headers,
            "url": self.normalize_url(action),
            "data": json.dumps(data),
            "params": params
        }

        request = httpx.Request(method, **kwargs)

        try:
            response = client.send(request)  
        except httpx.TimeoutException as exc:
            return {'status_code': 408}

        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return f"HTTP Exception for {exc.request.url} - {exc}"

        try:
            return json.loads(response.content)
        except Exception as e:
            return e

    def normalize_url(self, action):
        url = self.url.get() if APP_ENV!='production' else self.url
        return url + "/" + action
