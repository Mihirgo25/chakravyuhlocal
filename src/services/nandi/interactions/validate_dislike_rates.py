from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from fastapi import HTTPException
from micro_services.client import common
from datetime import datetime,timedelta
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
    
def validate_air_customs_unsatisfactory_rate_function(request):
    from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
    air_customs_rate = AirCustomsRate.select(AirCustomsRate.id,AirCustomsRate.updated_at).where(
        AirCustomsRate.id == request.get('rate_id')
    )
    if air_customs_rate.updated_at.date() < (datetime.now().date() - timedelta(days=30)):
        return {}
    return {}
def validate_fcl_customs_unsatisfactory_rate_function(request):
    from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
    fcl_customs_rate = FclCustomsRate.select(FclCustomsRate.id,FclCustomsRate.updated_at).where(
        FclCustomsRate.id == request.get('rate_id')
    )
    if fcl_customs_rate.updated_at.date() < (datetime.now().date() - timedelta(days=30)):
        return {}
    return {}
def validate_ltl_freight_unsatisfactory_rate_function(request):
    return {}
def validate_fcl_cfs_unsatisfactory_rate_function(request):
    from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
    fcl_cfs_rate = FclCfsRate.select(FclCfsRate.id,FclCfsRate.updated_at).where(
        FclCfsRate.id == request.get('rate_id')
    )
    if fcl_cfs_rate.updated_at.date() < (datetime.now().date() - timedelta(days=30)):
        return {}
    return {}
def validate_ftl_freight_unsatisfactory_rate_function(request):
    from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
    ftl_freight_rate = FtlFreightRate.select(FtlFreightRate.id,FtlFreightRate.updated_at).where(
        FtlFreightRate.id == request.get('rate_id')
    )
    if ftl_freight_rate.updated_at.date() < (datetime.now().date() - timedelta(days=30)):
        return {}
    return {}
def validate_lcl_freight_unsatisfactory_rate_function(request):
    return {}