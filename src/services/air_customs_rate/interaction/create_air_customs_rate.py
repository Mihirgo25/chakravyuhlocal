from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from database.db_session import db
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

def create_air_customs_rate(request):
    with db.atomic():
      return execute_transaction_code(request)

def execute_transaction_code(request):
  from celery_worker import air_customs_functions_delay

  request = {key: value for key, value in request.items() if value is not None}
  params = get_create_object_params(request)
  air_customs_rate = AirCustomsRate.select().where(
        AirCustomsRate.airport_id == request.get('airport_id'),
        AirCustomsRate.trade_type ==request.get('trade_type'),
        AirCustomsRate.service_provider_id == request.get('service_provider_id'),
        AirCustomsRate.commodity == request.get('commodity'),
        AirCustomsRate.rate_type == request.get('rate_type'),
    ).first()

  if not air_customs_rate:
    air_customs_rate = AirCustomsRate(**params)
    air_customs_rate.set_airport()
    air_customs_rate.set_location_ids()

  air_customs_rate.sourced_by_id = request.get("sourced_by_id")
  air_customs_rate.procured_by_id = request.get("procured_by_id")
  air_customs_rate.line_items = request.get('line_items')
  air_customs_rate.rate_not_available_entry = False

  air_customs_rate.validate_before_save()
  air_customs_rate.update_line_item_messages()

  try:
     air_customs_rate.save()
  except Exception as e:
      raise HTTPException(status_code=500, detail='Customs Rate did not save')

  create_audit(request, air_customs_rate.id)

  air_customs_functions_delay.apply_async(kwargs={'air_customs_object':air_customs_rate, 'request':request},queue = 'low')

  return {'id': air_customs_rate.id}

def get_create_object_params(request):
    return {
      'airport_id':request.get('airport_id'),
      'trade_type' : request.get('trade_type'),
      'service_provider_id': request.get('service_provider_id'),
      'commodity' : request.get('commodity'),
      'rate_type' : request.get('rate_type',DEFAULT_RATE_TYPE)
    }

def create_audit(request, customs_rate_id):
  audit_data = {
      'line_items': request.get('line_items')
  }

  AirCustomsRateAudit.create(
    object_id = customs_rate_id,
    object_type = 'AirCustomsRate',
    action_name = 'create',
    performed_by_id = request.get('performed_by_id'),
    rate_sheet_id = request.get('rate_sheet_id'),
    bulk_operation_id = request.get('bulk_operation_id'),
    data = audit_data
  )