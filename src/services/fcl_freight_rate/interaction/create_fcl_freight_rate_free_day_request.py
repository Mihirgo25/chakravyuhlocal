from services.fcl_freight_rate.models.fcl_freight_rate_free_day_request import FclFreightRateFreeDayRequest
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from database.db_session import db
from libs.logger import logger


def create_fcl_freight_rate_free_day_request(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            logger.error(e, exc_info = True)
            transaction.rollback()
            return e


def execute_transaction_code(request):
    row = {
        'source': request['source'],
        'source_id': request['source_id'],
        'performed_by_id': request['performed_by_id'],
        'performed_by_type': request['performed_by_type'],
        'performed_by_org_id': request['performed_by_org_id'],
        'free_days_type': request['free_days_type'],
        'service_provider_id': request['service_provider_id'],
        'location_id': request['location_id']
    }
    free_day_request = FclFreightRateFreeDayRequest.select().where(
        FclFreightRateFreeDayRequest.source == request['source'],
        FclFreightRateFreeDayRequest.source_id == request['source_id'],
        FclFreightRateFreeDayRequest.performed_by_id == request['performed_by_id'],
        FclFreightRateFreeDayRequest.performed_by_type == request['performed_by_type'],
        FclFreightRateFreeDayRequest.performed_by_org_id == request['performed_by_org_id'],
        FclFreightRateFreeDayRequest.free_days_type == request['free_days_type'],
        FclFreightRateFreeDayRequest.service_provider_id == request['service_provider_id'],
        FclFreightRateFreeDayRequest.location_id == request['location_id']).first()

    if not free_day_request:
        free_day_request = FclFreightRateFreeDayRequest(**row)

    create_params = {key:value for key,value in request.items() if key not in ['source', 'source_id', 'performed_by_id', 'performed_by_type', 'performed_by_org_id', 'free_days_type', 'service_provider_id', 'location_id']} | {'status': 'active'}
    for attr,value in create_params.items():
        setattr(free_day_request, attr, value)
    
    if check_validations(free_day_request):
        free_day_request.save()
    else:
        return 

    create_audit(request, free_day_request.id)

    return {
      'id': request.id
    }

def create_audit(request, free_day_request_id):
    performed_by_id = request['performed_by_id']
    del request['performed_by_id']

    FclFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = performed_by_id,
        data = request,
        object_id = free_day_request_id,
        object_type = 'FclFreightRateFreeDayRequest'   
    )

def check_validations(free_day_request):
    if free_day_request.validate_source() and free_day_request.validate_performed_by() and free_day_request.validate_performed_by_org() and free_day_request.validate_shipping_line_id() and free_day_request.validate_source_id():
        return True
    else:
        return False