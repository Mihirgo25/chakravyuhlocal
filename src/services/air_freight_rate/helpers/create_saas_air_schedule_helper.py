from micro_services.client import organization
from micro_services.client import common
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from configs.global_constants import DEFAULT_RATE_TYPE

def create_saas_air_schedule_airport_pair(air_object,request):
    origin_airport_id=request.get("origin_airport_id")
    destination_airport_id=request.get("destination_airport_id")
    airline_id = request.get('airline_id')
    air_freight_query = AirFreightRate.select(AirFreightRate.id).where(
        AirFreightRate.origin_airport_id == origin_airport_id,
        AirFreightRate.destination_airport_id == destination_airport_id,
        AirFreightRate.airline_id == airline_id,
        ~(AirFreightRate.rate_not_available_entry)
        )
    
    if not air_freight_query.exists():
        common.create_saas_air_schedule_airport_pair_coverages({"origin_airport_id":origin_airport_id, "destination_airport_id":destination_airport_id,"airline_id":airline_id})
