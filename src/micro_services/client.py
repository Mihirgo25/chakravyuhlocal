
from micro_services.common_client import CommonApiClient
from micro_services.auth_client import AuthApiClient
from micro_services.partner_client import PartnerApiClient
from micro_services.maps_client import MapsApiClient
from micro_services.spot_search_client import SpotSearchApiClient
from micro_services.checkout_client import CheckoutApiClient
from micro_services.shipment_client import ShipmentApiClient
from micro_services.development_client import DevelopmentApiClient
from configs.env import *

maps = organization = partner = spot_search = checkout = shipment = None

if APP_ENV == 'development':
    common = organization = partner = maps = spot_search = checkout = shipment  = DevelopmentApiClient()
else:
    common = CommonApiClient()
    organization = AuthApiClient()
    partner = PartnerApiClient()
    maps = MapsApiClient()
    spot_search = SpotSearchApiClient()
    checkout = CheckoutApiClient()
    shipment = ShipmentApiClient()
