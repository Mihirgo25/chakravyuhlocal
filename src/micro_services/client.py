
from micro_services.common_client import CommonApiClient
from micro_services.auth_client import AuthApiClient
from micro_services.partner_client import PartnerApiClient


common = CommonApiClient()
organization = AuthApiClient()
partner = PartnerApiClient()
