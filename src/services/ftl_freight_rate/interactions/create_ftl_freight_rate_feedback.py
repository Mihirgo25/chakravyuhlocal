from database.db_session import db
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from services.ftl_freight_rate.models.ftl_freight_rate_feedback import FtlFreightRateFeedback
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from datetime import datetime
from playhouse.postgres_ext import *
from fastapi import HTTPException
from micro_services.client import *



def create_ftl_freight_rate_feedback(request):
    return execute_transaction_code(request)

def execute_transaction_code(request):
    rate = FtlFreightRate.select().where(FtlFreightRate.id == request['rate_id']).first()
    if not rate:
        raise HTTPException(status_code=400, detail='{} is invalid'.format(request['rate_id']))
    
    row = {
        'status': 'active',
        'ftl_freight_rate_id': request['rate_id'],
        'source': request['source'],
        'source_id': request['source_id'],
        'performed_by_id': request['performed_by_id'],
        'performed_by_type': request['performed_by_type'],
        'performed_by_org_id': request['performed_by_org_id']
    }

    feedback = FtlFreightRateFeedback.select().where(
        FtlFreightRateFeedback.status == 'active',
        FtlFreightRateFeedback.ftl_freight_rate_id == request['rate_id'],
        FtlFreightRateFeedback.source == request['source'],
        FtlFreightRateFeedback.source_id == request['source_id'],
        FtlFreightRateFeedback.performed_by_id == request['performed_by_id'],
        FtlFreightRateFeedback.performed_by_type == request['performed_by_type'],
        FtlFreightRateFeedback.performed_by_org_id == request['performed_by_org_id']).first()
    
    if not feedback:
        feedback = FtlFreightRateFeedback(**row)

    create_params = get_create_params(request)
    for attr, value in create_params.items():
        setattr(feedback, attr, value)
    try:
        feedback.save()
    except:
        raise

    create_audit(request, feedback)

    return {'id': request['rate_id']}

def get_create_params(request):
    params =  {
        'feedbacks': request.get('feedbacks'),
        'remarks': request.get('remarks'),
        'preferred_freight_rate': request.get('preferred_freight_rate'),
        'preferred_freight_rate_currency': request.get('preferred_freight_rate_currency'),
        'feedback_type': request.get('feedback_type'),
        'booking_params': request.get('booking_params'),
        'status': 'active',
        'origin_location_id':request.get('origin_location_id'),
        'origin_country_id': request.get('origin_country_id'),
        'destination_location_id': request.get('destination_location_id'),
        'destination_country_id': request.get('destination_country_id'),
        'service_provider_id': request.get('service_provider_id'),
        'origin_location': request.get('origin_location'),
        'destination_location': request.get('destination_location')
    }
    return params

def create_audit(request, feedback):
    FtlFreightRateAudit.create(
        created_at = datetime.now(),
        updated_at = datetime.now(),
        object_type = 'FtlFreightRateFeedback',
        object_id = feedback.id,
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        data = {key:value for key,value in request.items() if key != 'performed_by_id'},
    )
