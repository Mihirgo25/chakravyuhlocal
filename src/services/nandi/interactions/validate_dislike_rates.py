from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from fastapi import HTTPException
from micro_services.client import common
def validate_freight_rate_feedback(request):
    rate=AirFreightRate.select(AirFreightRate.id,AirFreightRate.origin_airport_id,AirFreightRate.destination_airport_id,AirFreightRate.source).where(AirFreightRate.id==request['rate_id']).first()
    if not rate:
        raise HTTPException(status_code=404, detail='Rate Not Found')
    if 'unpreferred_operator' in request.get('feedbacks'):
        response = eval("validate_{}_unpreferred_operator_function".format(request.get('service_type')))
        
        
    if 'unsatisfactory_rate' in request.get('feedbacks'):
        if rate.source in ['predicted','rate_extension']:
            return {}


def validate_fcl_freight_unpreferred_operator_function():
    return {}

def validate_air_freight_unpreferred_operator_function(request):
    airport_id = {
        "origin_airport_id": request.get('origin_airport_id'),
        "destination_airport_id": request.get('destination_airport_id')
        }
    serviceable_airline_ids = common.get_saas_schedules_airport_pair_coverages(airport_id)
    if not (all(x in serviceable_airline_ids for x in request.get('preferred_airline_ids'))):
        return {}