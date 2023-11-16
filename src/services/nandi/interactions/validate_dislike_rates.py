from fastapi import HTTPException
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import asyncio

def validate_rate_feedback(request):
    response = {}

    if request.get('service_type') in ['haulage_freight','trailer_freight']:
        return response

    if 'unsatisfactory_rate' in request.get('feedbacks'):
        message = eval("validate_{}_unsatisfactory_rate_function(request)".format(request.get('service_type')))
        if message:
            response['unsatisfactory_rate'] = message
    return response

# def validate_fcl_freight_unpreferred_operator_function():
#     return {}

# def validate_air_freight_unpreferred_operator_function(request):
#     from micro_services.client import common
#     air_freight_rate = AirFreightRate.select(AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id).where(AirFreightRate.id == request.get("rate_id")).first()

#     airport_id = {
#         "origin_airport_id": str(air_freight_rate.origin_airport_id),
#         "destination_airport_id": str(air_freight_rate.destination_airport_id)
#         }
#     serviceable_airline_ids = common.get_saas_schedules_airport_pair_coverages(airport_id)
#     serviceable_airlines =0
#     unserviceable_airlines = 0
#     for preferred_airline in request.get('preferred_operator_ids'):
#         if preferred_airline in serviceable_airline_ids:
#             serviceable_airlines = serviceable_airlines+1
#         else:
#             unserviceable_airlines = unserviceable_airlines +1

#     if serviceable_airlines ==0 and unserviceable_airlines!=0:
#         return {'message': 'Rates for all  Airlines that are serviceable on this Airport pair are present'}

#     return {}

def validate_air_freight_rate_local_unsatisfactory_rate_function(request):
    from services.air_freight_rate.models.air_freight_rate_local_feedback import AirFreightRateLocalFeedback
    air_locals_rate = AirFreightRateLocalFeedback.select(AirFreightRateLocalFeedback.id,AirFreightRateLocalFeedback.updated_at).where(
        AirFreightRateLocalFeedback.id == request.get('rate_id')
    ).first()

    if air_locals_rate.updated_at.date() > (datetime.now().date() - timedelta(days=30)):
        return {'message': 'Best available rate for this port pair'}
    return {}

def validate_fcl_freight_rate_local_unsatisfactory_rate_function(request):
    from services.fcl_freight_rate.models.fcl_freight_rate_local_feedback import FclFreightRateLocalFeedback
    fcl_locals_rate = FclFreightRateLocalFeedback.select(FclFreightRateLocalFeedback.id,FclFreightRateLocalFeedback.updated_at).where(
        FclFreightRateLocalFeedback.id == request.get('rate_id')
    ).first()

    if fcl_locals_rate.updated_at.date() > (datetime.now().date() - timedelta(days=30)):
        return {'message': 'Best available rate for this port pair'}
    return {}

def validate_air_customs_unsatisfactory_rate_function(request):
    from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
    air_customs_rate = AirCustomsRate.select(AirCustomsRate.id,AirCustomsRate.updated_at).where(
        AirCustomsRate.id == request.get('rate_id')
    ).first()

    if air_customs_rate.updated_at.date() > (datetime.now().date() - timedelta(days=30)):
        return {'message': 'Best available rate for this port pair'}
    return {}

def validate_fcl_customs_unsatisfactory_rate_function(request):
    from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
    fcl_customs_rate = FclCustomsRate.select(FclCustomsRate.id,FclCustomsRate.updated_at).where(
        FclCustomsRate.id == request.get('rate_id')
    ).first()

    if fcl_customs_rate.updated_at.date() > (datetime.now().date() - timedelta(days=30)):
        return {'message': 'Best available rate for this port pair'}
    return {}

def validate_ltl_freight_unsatisfactory_rate_function(request):
    from micro_services.client import common
    ltl_freight_rates = common.list_ltl_freight_rates({'filters': {'id': request.get('rate_id')}})
    if ltl_freight_rates.get('list') and len(ltl_freight_rates['list']) > 0:
        ltl_freight_rate = ltl_freight_rates['list'][0]
        if ltl_freight_rate['updated_at'].date() > (datetime.now().date() - timedelta(days=30)):
            return {'message': 'Best available rate for this port pair'}
    return {}

def validate_fcl_cfs_unsatisfactory_rate_function(request):
    from services.fcl_cfs_rate.models.fcl_cfs_rate import FclCfsRate
    fcl_cfs_rate = FclCfsRate.select(FclCfsRate.id,FclCfsRate.updated_at).where(
        FclCfsRate.id == request.get('rate_id')
    ).first()

    if fcl_cfs_rate.updated_at.date() > (datetime.now().date() - timedelta(days=30)):
        return {'message': 'Best available rate for this port pair'}
    return {}

def validate_ftl_freight_unsatisfactory_rate_function(request):
    from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
    ftl_freight_rate = FtlFreightRate.select(FtlFreightRate.id,FtlFreightRate.updated_at).where(
        FtlFreightRate.id == request.get('rate_id')
    ).first()

    if ftl_freight_rate.updated_at.date() > (datetime.now().date() - timedelta(days=30)):
        return {'message': 'Best available rate for this port pair'}
    return {}

def validate_lcl_freight_unsatisfactory_rate_function(request):
    from micro_services.client import common
    lcl_freight_rates = common.list_lcl_freight_rates({'filters': {'id': request.get('rate_id')}})
    if lcl_freight_rates.get('list') and len(lcl_freight_rates['list']) > 0:
        lcl_freight_rate = lcl_freight_rates['list'][0]
        if lcl_freight_rate['updated_at'].date() > (datetime.now().date() - timedelta(days=30)):
            return {'message': 'Best available rate for this port pair'}
    return {}

def validate_lcl_freight_rate_local_unsatisfactory_rate_function(request):
    from micro_services.client import common
    lcl_freight_local_rates = common.list_lcl_freight_rate_locals({'filters': {'id': request.get('rate_id')}})
    if lcl_freight_local_rates.get('list') and len(lcl_freight_local_rates['list']) > 0:
        lcl_freight_local_rate = lcl_freight_local_rates['list'][0]
        if lcl_freight_local_rate['updated_at'].date() > (datetime.now().date() - timedelta(days=30)):
            return {'message': 'Best available rate for this port pair'}
    return {}

def validate_lcl_customs_unsatisfactory_rate_function(request):
    from micro_services.client import common
    lcl_customs_rates = common.list_lcl_customs_rates({'filters': {'id': request.get('rate_id')}})
    if lcl_customs_rates.get('list') and len(lcl_customs_rates['list']) > 0:
        lcl_customs_rate = lcl_customs_rates['list'][0]
        if lcl_customs_rate['updated_at'].date() > (datetime.now().date() - timedelta(days=30)):
            return {'message': 'Best available rate for this port pair'}
    return {}

def validate_fcl_freight_unsatisfactory_rate_function(request):
    from services.fcl_freight_rate.models.fcl_freight_rate_feedback import FclFreightRateFeedback

    feedback = FclFreightRateFeedback.select(FclFreightRateFeedback.status,FclFreightRateFeedback.reverted_validities,FclFreightRateFeedback.updated_at).where(FclFreightRateFeedback.fcl_freight_rate_id == request['rate_id'], FclFreightRateFeedback.feedback_type == 'disliked').order_by(FclFreightRateFeedback.updated_at.desc()).first()

    if feedback:
        if feedback.reverted_validities and feedback.updated_at.date() == datetime.now().date():
            return {'message': 'Best available rate for this port pair'}
        elif feedback.status == 'active':
            return {}

    from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate

    fcl_freight_rate = FclFreightRate.select(FclFreightRate.id, FclFreightRate.origin_port_id, FclFreightRate.destination_port_id, FclFreightRate.shipping_line_id, FclFreightRate.container_size, FclFreightRate.container_type, FclFreightRate.commodity, FclFreightRate.rate_type, FclFreightRate.mode, FclFreightRate.updated_at).where(FclFreightRate.id == request['rate_id']).first()

    if not fcl_freight_rate:
        raise HTTPException(status_code=404, detail='Fcl Freight Rate Not Found')
    
    rate_type = fcl_freight_rate.rate_type
    mode = fcl_freight_rate.mode

    if rate_type == 'promotional':
        return {'message': 'This is a Promotional Rate'}

    elif mode in ['predicted', 'rate_extension', 'cluster_extension']:
        return {}

    elif mode == 'flash_booking':
        if fcl_freight_rate.updated_at > datetime.now() - timedelta(hours=4):
            return {'message': 'Best available rate for this port pair'}
        else:
            return {}

    elif mode in ['rms_upload', 'forcasted_rfq','rate_sheet','disliked_rate','missing_rate']:
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
            "origin_port_id": str(fcl_freight_rate.origin_port_id),
            "destination_port_id": str(fcl_freight_rate.destination_port_id),
            "shipping_line_id": str(fcl_freight_rate.shipping_line_id),
            "container_size": fcl_freight_rate.container_size,
            "container_type": fcl_freight_rate.container_type,
            "commodity": fcl_freight_rate.commodity,
            "query_type": "average_price",
            "validity_end_less_than": str(datetime.now().date()),
            "validity_end_greater_than": str(datetime.now().date() - relativedelta(months=3))
        }
        fcl_freight_rates = asyncio.run(list_fcl_freight_rate_statistics(filters = filters, page_limit = 10, page = 1, is_service_object_required = False))

        if not len(fcl_freight_rates.get('list') or []):
            return {}
        
        avg_price = fcl_freight_rates['list'][0]['average_standard_price']
        sigma = fcl_freight_rates['list'][0]['bas_standard_price_deviation'] 

        lower_bound = avg_price - 0.1 * sigma
        upper_bound = avg_price + 0.1 * sigma

        bas_standard_price = request.get('standard_price')

        if bas_standard_price > lower_bound and bas_standard_price < upper_bound:
            return {'message': 'Best available rate for this port pair'}
        else:
            return {}
    else:
        return {}

def validate_air_freight_unsatisfactory_rate_function(request):
    from services.air_freight_rate.models.air_freight_rate_feedback import AirFreightRateFeedback

    feedback = AirFreightRateFeedback.select(AirFreightRateFeedback.reverted_rate,AirFreightRateFeedback.updated_at,AirFreightRateFeedback.status).where(AirFreightRateFeedback.air_freight_rate_id == request['rate_id'], AirFreightRateFeedback.feedback_type == 'disliked').order_by(AirFreightRateFeedback.updated_at.desc()).first()

    if feedback:
        if feedback.reverted_rate and feedback.updated_at.date() == datetime.now().date():
            return {'message': 'Best available rate for this port pair'}
        elif feedback.status == 'active':
            return {}

    from services.air_freight_rate.models.air_freight_rate import AirFreightRate

    air_freight_rate = AirFreightRate.select(AirFreightRate.id, AirFreightRate.origin_airport_id, AirFreightRate.destination_airport_id, AirFreightRate.airline_id, AirFreightRate.commodity, AirFreightRate.commodity_type, AirFreightRate.rate_type, AirFreightRate.source, AirFreightRate.updated_at).where(AirFreightRate.id == request['rate_id']).first()

    if not air_freight_rate:
        raise HTTPException(status_code=404, detail='Air Freight Rate Not Found')

    rate_type = air_freight_rate.rate_type
    source = air_freight_rate.source

    if rate_type == 'promotional':
        return {'message': 'This is a Promotional Rate'}

    elif source in ['predicted', 'rate_extension']:
        return {}

    elif source == 'flash_booking':
        if air_freight_rate.updated_at > datetime.now() - timedelta(hours=4):
            return {'message': 'Best available rate for this port pair'}
        else:
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
            "origin_airport_id": str(air_freight_rate.origin_airport_id),
            "destination_airport_id": str(air_freight_rate.destination_airport_id),
            "airline_id": str(air_freight_rate.airline_id),
            "rate_type": rate_type,
            "commodity": air_freight_rate.commodity,
            "commodity_type": air_freight_rate.commodity_type,
            "chargeable_weight": request.get("chargeable_weight"),
            "query_type": "aggregate",
            "validity_end_less_than": str(datetime.now().date()),
            "validity_end_greater_than": str(datetime.now().date() - relativedelta(months=3))
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
            return {}