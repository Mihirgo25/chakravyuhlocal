import httpx
from configs.env import *
import json

class GlobalClient:
    def __init__(self, url,headers):
        self.client = httpx.Client()
        self.url = url
        self.headers = headers

    def request(self, method, action, data={}, params={}):
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
        return self.url + "/" + action
