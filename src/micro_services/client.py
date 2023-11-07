
from micro_services.common_client import CommonApiClient
from micro_services.auth_client import AuthApiClient
from micro_services.partner_client import PartnerApiClient
from micro_services.maps_client import MapsApiClient
from micro_services.spot_search_client import SpotSearchApiClient
from micro_services.checkout_client import CheckoutApiClient
from micro_services.shipment_client import ShipmentApiClient
from micro_services.development_client import DevelopmentApiClient
from micro_services.loki_client import LokiApiClient
from micro_services.schedule_client import ScheduleApiClient
from micro_services.debezium_connect_client import DebeziumConnectApiClient
from configs.env import APP_ENV
from enums.global_enums import AppEnv, Context

maps = organization = partner = spot_search = checkout = shipment = debezium_connect = loki = schedule_client = None
if APP_ENV != AppEnv.production:
    common = organization = partner = maps = spot_search = checkout = shipment = loki  = schedule_client = DevelopmentApiClient(context = Context.common)
    debezium_connect = DebeziumConnectApiClient()
    
else:
    common = CommonApiClient()
    organization = AuthApiClient()
    partner = PartnerApiClient()
    maps = MapsApiClient()
    spot_search = SpotSearchApiClient()
    checkout = CheckoutApiClient()
    shipment = ShipmentApiClient()
    loki = LokiApiClient()
    debezium_connect = DebeziumConnectApiClient()
    schedule_client =ScheduleApiClient()
    
