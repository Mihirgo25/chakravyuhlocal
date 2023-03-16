from services.fcl_freight_rate.models.fcl_freight_rate_free_day_request import FclFreightRateFreeDayRequest
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.helpers.find_or_initialize import find_or_initialize
from datetime import datetime
from database.db_session import db
from libs.logger import logger

def create_fcl_freight_rate_free_day_request(request):
    with db.atomic() as transaction:
        try:
            data = execute_transaction_code(request)
        except Exception as e:
            logger.error(e, exc_info = True)
            transaction.rollback()
            return 'Creation Failed'


def execute_transaction_code(request):
    object_params = get_unique_object_params(request)
    free_day_request = find_or_initialize(FclFreightRateFreeDayRequest, **object_params)

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

def get_unique_object_params(request):
    return {
    'source': request['source'],
    'source_id': request['source_id'],
    'performed_by_id': request['performed_by_id'],
    'performed_by_type': request['performed_by_type'],
    'performed_by_org_id': request['performed_by_org_id'],
    'free_days_type': request['free_days_type'],
    'service_provider_id': request['service_provider_id'],
    'location_id': request['location_id']
    }

def create_audit(request, free_day_request_id):
    del request['performed_by_id']

    FclFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        data = request,
        object_id = free_day_request_id,
        object_type = 'FclFreightRateFreeDayRequest'   
    )

def find_or_initialize(**kwargs):
  try:
    obj = FclFreightRateFreeDayRequest.get(**kwargs)
    obj.updated_at = datetime.now()
  except FclFreightRateFreeDayRequest.DoesNotExist:
    obj = FclFreightRateFreeDayRequest(**kwargs)
  return obj

def check_validations(free_day_request):
    if free_day_request.validate_source() and free_day_request.validate_performed_by() and free_day_request.validate_performed_by_org() and free_day_request.validate_shipping_line_id() and free_day_request.validate_source_id():
        return True
    else:
        return False