from peewee import *
from database.db_session import db
from services.fcl_cfs_rate.models.fcl_cfs_rate_request import FclCfsRateRequest
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from fastapi import HTTPException
from services.fcl_cfs_rate.fcl_cfs_celery_worker import send_notifications_to_supply_agents_cfs_request_delay
from libs.get_multiple_service_objects import get_multiple_service_objects
from services.fcl_cfs_rate.interaction.create_fcl_cfs_rate_job import create_fcl_cfs_rate_job


def create_fcl_cfs_rate_request(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    search_params = {
        'source': request.get('source'),
        'source_id': request.get('source_id'),
        'performed_by_id': request.get('performed_by_id'),
        'performed_by_type': request.get('performed_by_type'),
        'performed_by_org_id': request.get('performed_by_org_id')
    }

    cfs_request = FclCfsRateRequest.select().where(
        FclCfsRateRequest.source == request.get('source'),
        FclCfsRateRequest.source_id == request.get('source_id'),
        FclCfsRateRequest.performed_by_id == request.get('performed_by_id'),
        FclCfsRateRequest.performed_by_type == request.get('performed_by_type'),
        FclCfsRateRequest.performed_by_org_id == request.get('performed_by_org_id'),
         FclCfsRateRequest.trade_type == request.get('trade_type')).first()

    if not cfs_request:
        cfs_request = FclCfsRateRequest(**search_params)
        next_sequence_value = db.execute_sql("SELECT nextval('fcl_cfs_rate_request_serial_id_seq'::regclass)").fetchone()[0]
        setattr(cfs_request,'serial_id',next_sequence_value)

    create_params = get_create_params(request)
    for attr, value in create_params.items():
        setattr(cfs_request, attr, value)
    cfs_request.set_port()
    cfs_request.set_spot_search()

    try:
        cfs_request.save()
    except :
      raise HTTPException(status_code=500, detail='CFS Request did not save')


    create_audit_for_cfs_request(request, cfs_request.id)
    get_multiple_service_objects(cfs_request)
    send_notifications_to_supply_agents_cfs_request_delay.apply_async(kwargs={'object':cfs_request}, queue = 'low')

    request["source_id"] = cfs_request.id
    request['serial_id'] = cfs_request.serial_id
    create_fcl_cfs_rate_job(request, "rate_request")

    return {'id': cfs_request.id}

def get_create_params(request):
    return {
        'preferred_rate': request.get('preferred_rate'),
        'preferred_rate_currency': request.get('preferred_rate_currency'),
        'cargo_readiness_date': request.get('cargo_readiness_date'),
        'remarks': request.get('remarks'),
        'booking_params': request.get('booking_params'),
        'container_size': request.get('container_size'),
        'commodity': request.get('commodity'),
        'country_id': request.get('country_id'),
        'port_id': request.get('port_id'),
        'trade_type': request.get('trade_type'),
        'status': 'active'
    }

def create_audit_for_cfs_request(request,cfs_request_id):
    performed_by_id = request.get('performed_by_id')
    del request['performed_by_id']
    if request.get('cargo_readiness_date'):
        request['cargo_readiness_date'] = request.get('cargo_readiness_date').isoformat()
    
    FclCfsRateAudit.create(
        object_id = cfs_request_id,
        action_name = 'create',
        performed_by_id = performed_by_id,
        data = request,
        object_type = 'FclCfsRateRequest'
    )