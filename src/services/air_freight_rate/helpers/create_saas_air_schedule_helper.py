from micro_services.client import organization
from micro_services.client import common
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from configs.global_constants import DEFAULT_RATE_TYPE

def create_saas_air_schedule_airport_pair(air_object,request):
    from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
    service_provider_id=request.get("service_provider_id")
    origin_airport_id=request.get("origin_airport_id")
    destination_airport_id=request.get("destination_airport_id")

    if not AirFreightRate.select(AirFreightRate.id).where(AirFreightRate.service_provider_id==service_provider_id,
                                                          AirFreightRate.rate_not_available_entry==False,
                                                          AirFreightRate.rate_type==DEFAULT_RATE_TYPE).exists():
        common.create_saas_air_schedule_airport_pair({"origin_airport_id":origin_airport_id, "destination_airport_id":destination_airport_id})
        get_multiple_service_objects(air_object)