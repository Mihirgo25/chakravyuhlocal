from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from fastapi import HTTPException
from micro_services.client import common
from datetime import datetime, timedelta
import asyncio

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
        return {'message': 'Rates for all Shipping lines that are serviceable on this port pair are present'}
    return {}
    
def validate_air_customs_unsatisfactory_rate_function(request):
    from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
    air_customs_rate = AirCustomsRate.select(AirCustomsRate.id,AirCustomsRate.updated_at).where(
        AirCustomsRate.id == request.get('rate_id')
    ).order_by(AirCustomsRate.updated_at.desc()).first()

    if air_customs_rate.updated_at.date() < (datetime.now().date() - timedelta(days=30)):
        return {}
    return {}

def validate_fcl_customs_unsatisfactory_rate_function(request):
    from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
    fcl_customs_rate = FclCustomsRate.select(FclCustomsRate.id,FclCustomsRate.updated_at).where(
        FclCustomsRate.id == request.get('rate_id')
    ).order_by(FclCustomsRate.updated_at.desc()).first()

    if fcl_customs_rate.updated_at.date() < (datetime.now().date() - timedelta(days=30)):
        return {}
    return {}

def validate_ltl_freight_unsatisfactory_rate_function(request):
    return {}

def validate_fcl_cfs_unsatisfactory_rate_function(request):
    from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
    fcl_cfs_rate = FclCfsRate.select(FclCfsRate.id,FclCfsRate.updated_at).where(
        FclCfsRate.id == request.get('rate_id')
    ).order_by(FclCfsRate.updated_at.desc()).first()

    if fcl_cfs_rate.updated_at.date() < (datetime.now().date() - timedelta(days=30)):
        return {}
    return {}

def validate_ftl_freight_unsatisfactory_rate_function(request):
    from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
    ftl_freight_rate = FtlFreightRate.select(FtlFreightRate.id,FtlFreightRate.updated_at).where(
        FtlFreightRate.id == request.get('rate_id')
    ).order_by(FtlFreightRate.updated_at.desc()).first()

    if ftl_freight_rate.updated_at.date() < (datetime.now().date() - timedelta(days=30)):
        return {}
    return {}

def validate_lcl_freight_unsatisfactory_rate_function(request):
    return {}
    
def validate_fcl_freight_unsatisfactory_rate_function(request):
    from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback

    feedback = FclFreightRateFeedback.select().where(FclFreightRateFeedback.fcl_freight_rate_id == request['rate_id'], FclFreightRateFeedback.feedback_type == 'disliked').order_by(FclFreightRateFeedback.updated_at.desc()).first()

    if feedback:
        if feedback.get('reverted_validities') and feedback.get('updated_at') > datetime.now() - timedelta(days=4):
            return {'message': 'Best available rate for this port pair'}
        else:
            ### create job
            return {}

    fcl_freight_rate = FclFreightRate.select(FclFreightRate.id, FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.origin_main_port_id, FclFreightRate.destination_main_port_id, FclFreightRate.shipping_line_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.rate_type, FclFreightRate.mode, FclFreightRate.updated_at).where(FclFreightRate.id == request['rate_id']).first()

    if not fcl_freight_rate:
        raise HTTPException(status_code=404, detail='Fcl Freight Rate Not Found')
    
    rate_type = fcl_freight_rate.rate_type
    mode = fcl_freight_rate.mode

    if rate_type == 'promotional':
        return {'message': 'This is a Promotional Rate'}

    elif mode in ['predicted', 'rate_extension', 'cluster_extension']:
        ### create job
        return {}
    
    elif mode == 'flash_booking':
        if fcl_freight_rate.updated_at > datetime.now() - timedelta(hours=4):
            return {'message': 'Best available rate for this port pair'}
        else:
            ### create job
            return {}
    
    elif mode in ['rms_upload', 'forcasted_rfq']:
        from services.bramhastra.interactions.list_fcl_freight_rate_statistics import list_fcl_freight_rate_statistics

        filters = {
            "group_by":[
                "origin_port_id",
                "destination_port_id",
                "origin_main_port_id",
                "destination_main_port_id",
                "shipping_line_id",
                "container_size",
                "container_type",
                "commodity"
            ],
            "origin_port_id": fcl_freight_rate.origin_port_id,
            "destination_port_id": fcl_freight_rate.destination_port_id,
            "origin_main_port_id": fcl_freight_rate.origin_main_port_id,
            "destination_main_port_id": fcl_freight_rate.destination_main_port_id,
            "shipping_line_id": fcl_freight_rate.shipping_line_id,
            "container_size": fcl_freight_rate.container_size,
            "container_type": fcl_freight_rate.container_type,
            "commodity": fcl_freight_rate.commodity,
            "query_type": "average_price",
            "validity_end_less_than": str(datetime.now().date()),
            "validity_end_greater_than": str(datetime.now().date() - timedelta(months=3))
        }
        fcl_freight_rates = asyncio.run(list_fcl_freight_rate_statistics(filters = filters, page_limit = 10, page = 1, is_service_object_required = False))

        if not len(fcl_freight_rates.get('list') or []):
            return {}
        
        avg_price = fcl_freight_rates['list'][0]['average_standard_price']
        sigma = fcl_freight_rates['list'][0]['bas_standard_price_deviation'] 

        lower_bound = avg_price - 0.1 * sigma
        upper_bound = avg_price + 0.1 * sigma

        bas_standard_price = request.get('bas_standard_price') ## later

        if bas_standard_price > lower_bound and bas_standard_price < upper_bound:
            return {'message': 'Best available rate for this port pair'}
        else:
            ### create job
            return {}

def validate_air_freight_unsatisfactory_rate_function(request):
    from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback

    feedback = AirFreightRateFeedback.select().where(AirFreightRateFeedback.air_freight_rate_id == request['rate_id'], AirFreightRateFeedback.feedback_type == 'disliked').order_by(AirFreightRateFeedback.updated_at.desc()).first()

    if feedback:
        if feedback.get('status') == 'inactive' and feedback.get('updated_at') > datetime.now() - timedelta(days=4):
            return {'message': 'Best available rate for this port pair'}
        else:
            ### create job
            return {}

    air_freight_rate = AirFreightRate.select(AirFreightRate.id, AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id, AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id, AirFreightRate.airline_id, AirFreightRate.commodity, AirFreightRate.commodity_type, AirFreightRate.rate_type, AirFreightRate.source, AirFreightRate.updated_at).where(AirFreightRate.id == request['rate_id']).first()

    if not air_freight_rate:
        raise HTTPException(status_code=404, detail='Air Freight Rate Not Found')
    
    rate_type = air_freight_rate.rate_type
    source = air_freight_rate.source

    if rate_type == 'promotional':
        return {'message': 'This is a Promotional Rate'}

    elif source in ['predicted', 'rate_extension']:
        ### create job
        return {}
    
    elif source == 'flash_booking':
        if air_freight_rate.updated_at > datetime.now() - timedelta(hours=4):
            return {'message': 'Best available rate for this port pair'}
        else:
            ### create job
            return {}
    
    else:
        from services.bramhastra.interactions.list_air_freight_rate_statistics import list_air_freight_rate_statistics
        filters = {
            "group_by":[
                "origin_airport_id",
                "destination_airport_id",
                "airline_id"
            ],
            "select":[
                "origin_airport_id",
                "destination_airport_id",
                "airline_id"
            ],
            "origin_airport_id": air_freight_rate.origin_airport_id,
            "destination_airport_id": air_freight_rate.destination_airport_id,
            "airline_id": air_freight_rate.airline_id,
            "rate_type": rate_type,
            "commodity": air_freight_rate.commodity,
            "commodity_type": air_freight_rate.commodity_type,
            "chargeable_weight": request.get("chargeable_weight"),
            "query_type": "aggregate",
            "validity_end_less_than": str(datetime.now().date()),
            "validity_end_greater_than": str(datetime.now().date() - timedelta(months=3))
        }

        air_freight_rates = asyncio.run(list_air_freight_rate_statistics(filters = filters, page_limit = 10, page = 1, is_service_object_required = False,pagination_data_required=False))

        if not len(air_freight_rates.get('list') or []):
            return {}
        
        avg_price = air_freight_rates['list'][0]['standard_price']
        sigma = air_freight_rates['list'][0]['standard_price_deviation']

        lower_bound = avg_price - 0.1 * sigma
        upper_bound = avg_price + 0.1 * sigma

        bas_standard_price = request.get('standard_price')

        if bas_standard_price > lower_bound and bas_standard_price < upper_bound:
            return {'message': 'Best available rate for this port pair'}
        else:
            ### create job
            return {}