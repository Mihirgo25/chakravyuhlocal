from configs.env import RUBY_ADDRESS_URL
from rails_client.ruby_client import RubyClient

class RubyApiClient:
    def __init__(self):
        self.client=RubyClient(str(RUBY_ADDRESS_URL))

    def list_locations(self,data={}):
        return self.client.request('GET','list_locations',data)

