from configs.env import RUBY_AUTHTOKEN,RUBY_AUTHSCOPE,RUBY_AUTHSCOPEID
from micro_services.global_client import GlobalClient
from micro_services.discover_client import get_instance_url
from micro_services.auth_client import AuthApiClient
from micro_services.checkout_client import CheckoutApiClient
from micro_services.common_client import CommonApiClient
from micro_services.spot_search_client import SpotSearchApiClient
from micro_services.partner_client import PartnerApiClient
from micro_services.shipment_client import ShipmentApiClient
from micro_services.maps_client import MapsApiClient


class DevelopmentApiClient(CommonApiClient,AuthApiClient,CheckoutApiClient,SpotSearchApiClient,PartnerApiClient,ShipmentApiClient,MapsApiClient):
    def __init__(self):
        self.client=GlobalClient(url = str(get_instance_url('common')),headers={
            "Authorization": "Bearer: " + RUBY_AUTHTOKEN,
            "AuthorizationScope": RUBY_AUTHSCOPE,
            "AuthorizationScopeId": RUBY_AUTHSCOPEID,
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def reset_context_var(self,url):
        self.client.url.set(url)