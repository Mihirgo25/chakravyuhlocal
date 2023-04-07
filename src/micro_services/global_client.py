import httpx
from configs.env import *
import json
from fastapi.encoders import jsonable_encoder
from contextvars import ContextVar
class GlobalClient:
    def __init__(self, url,headers):
        self.client = httpx.Client()
        if APP_ENV !='production':
            self.url = ContextVar('client_base_url', default=RUBY_ADDRESS_URL)
        else:
            self.url = url
        self.headers = headers

    def request(self, method, action, data={}, params={}):
        if isinstance(data, dict):
            data = jsonable_encoder(data)
        kwargs = {
            "headers": self.headers,
            "url": self.normalize_url(action),
            "data": json.dumps(data),
            "params": params
        }

        request = httpx.Request(method, **kwargs)


        response = self.client.send(request)

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
