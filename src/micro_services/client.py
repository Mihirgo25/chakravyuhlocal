
from micro_services.common_client import CommonApiClient
from micro_services.auth_client import AuthApiClient
from micro_services.partner_client import PartnerApiClient
from micro_services.maps_client import MapsApiClient
from micro_services.spot_search_client import SpotSearchApiClient
from micro_services.checkout_client import CheckoutApiClient


common = CommonApiClient()
organization = AuthApiClient()
partner = PartnerApiClient()
maps = MapsApiClient()
spot_search = SpotSearchApiClient()
checkout = CheckoutApiClient()
