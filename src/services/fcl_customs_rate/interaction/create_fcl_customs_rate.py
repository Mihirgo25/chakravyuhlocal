from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from database.db_session import db
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

def create_fcl_customs_rate(request):
    with db.atomic():
      return execute_transaction_code(request)

def execute_transaction_code(request):
  from celery_worker import fcl_customs_functions_delay
  request = {key: value for key, value in request.items() if value is not None}
  params = get_create_object_params(request)
  customs_rate = FclCustomsRate.select().where(
        FclCustomsRate.location_id == request.get('location_id'),
        FclCustomsRate.trade_type ==request.get('trade_type'),
        FclCustomsRate.container_size== request.get('container_size'),
        FclCustomsRate.container_type==request.get('container_type'),
        FclCustomsRate.commodity == request.get('commodity'),
        FclCustomsRate.service_provider_id==request.get('service_provider_id'),
        FclCustomsRate.importer_exporter_id == request.get('importer_exporter_id'),
        FclCustomsRate.rate_type == request.get('rate_type')).first()
      
  if not customs_rate:
    customs_rate = FclCustomsRate(**params)

  customs_rate.sourced_by_id = request.get("sourced_by_id")
  customs_rate.procured_by_id = request.get("procured_by_id")
  customs_rate.customs_line_items = request.get('customs_line_items')
  customs_rate.cfs_line_items = request.get('cfs_line_items')
  customs_rate.zone_id = request.get('zone_id')
  customs_rate.set_platform_price()
  customs_rate.set_is_best_price()

  customs_rate.update_customs_line_item_messages()
  customs_rate.set_location_ids()
  customs_rate.validate_before_save()
  
  try:
     customs_rate.save()
  except Exception as e:
      raise HTTPException(status_code=500, detail='Customs Rate did not save')

  if not customs_rate.importer_exporter_id:
    customs_rate.delete_rate_not_available_entry()

  create_audit(request, customs_rate.id)

  customs_rate.update_platform_prices_for_other_service_providers()
  fcl_customs_functions_delay.apply_async(kwargs={'fcl_customs_object':customs_rate, 'request':request},queue = 'low')

  return {'id': customs_rate.id}

def get_create_object_params(request):
    return {
      'location_id':request.get('location_id'),
      'trade_type' : request.get('trade_type'),
      'container_size' : request.get('container_size'),
      'container_type' : request.get('container_type'),
      'service_provider_id': request.get('service_provider_id'),
      'commodity' : request.get('commodity'),
      'importer_exporter_id' : request.get('importer_exporter_id'),
      'accuracy': request.get('accuracy', 100),
      'mode' : request.get('mode','manual'),
      "rate_type" : request.get('rate_type', DEFAULT_RATE_TYPE)
    }

def create_audit(request, customs_rate_id):
  audit_data = {
      'customs_line_items': request.get('customs_line_items')
  }

  FclCustomsRateAudit.create(
    object_id = customs_rate_id,
    object_type = 'FclCustomsRate',
    action_name = 'create',
    performed_by_id = request.get('performed_by_id'),
    rate_sheet_id = request.get('rate_sheet_id'),
    data = audit_data
  )