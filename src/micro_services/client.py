
from micro_services.common_client import CommonApiClient
from micro_services.auth_client import AuthApiClient
from micro_services.partner_client import PartnerApiClient
from micro_services.maps_client import MapsApiClient
from micro_services.spot_search_client import SpotSearchApiClient
from micro_services.checkout_client import CheckoutApiClient
from micro_services.shipment_client import ShipmentApiClient
from micro_services.development_client import DevelopmentApiClient
from micro_services.loki_client import LokiApiClient
from configs.env import APP_ENV

maps = organization = partner = spot_search = checkout = shipment = loki =  None

if APP_ENV != 'production':
    common = organization = partner = maps = spot_search = checkout = shipment = loki = DevelopmentApiClient()
else:
    common = CommonApiClient()
    organization = AuthApiClient()
    partner = PartnerApiClient()
    maps = MapsApiClient()
    spot_search = SpotSearchApiClient()
    checkout = CheckoutApiClient()
    shipment = ShipmentApiClient()
    loki = LokiApiClient()
