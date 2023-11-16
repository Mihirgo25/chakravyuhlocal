from micro_services.client import organization
from micro_services.client import common
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from configs.global_constants import DEFAULT_RATE_TYPE

def create_saas_air_schedule_airport_pair(air_object,request):
    origin_airport_id=request.get("origin_airport_id")
    destination_airport_id=request.get("destination_airport_id")
    airline_id = request.get('airline_id')
   
    common.create_saas_air_schedule_airport_pair_coverage({"origin_airport_id":origin_airport_id, "destination_airport_id":destination_airport_id,"airline_id":airline_id,"source":"supply","is_verified":True})
