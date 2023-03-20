
from micro_services.common_client import CommonApiClient
from micro_services.auth_client import AuthApiClient
from micro_services.partner_client import PartnerApiClient
from micro_services.maps_client import MapsApiClient


common = CommonApiClient()
organization = AuthApiClient()
partner = PartnerApiClient()
maps = MapsApiClient()
