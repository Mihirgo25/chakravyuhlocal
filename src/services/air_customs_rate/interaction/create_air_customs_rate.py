from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from database.db_session import db
from fastapi import HTTPException

def create_air_customs_rate_data(request):
    with db.atomic():
      return create_air_customs_rate(request)

def create_air_customs_rate(request):
  from celery_worker import delay_air_customs_functions

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
    air_customs_rate.set_location()
    air_customs_rate.set_location_ids()

  air_customs_rate.sourced_by_id = request.get("sourced_by_id")
  air_customs_rate.procured_by_id = request.get("procured_by_id")
  air_customs_rate.line_items = request.get('line_items')

  air_customs_rate.update_customs_line_item_messages()
  air_customs_rate.validate_before_save()

  try:
     air_customs_rate.save()
  except Exception as e:
      raise HTTPException(status_code=500, detail='Customs Rate did not save')

  create_audit(request, air_customs_rate.id)

  air_customs_rate.update_platform_prices_for_other_service_providers()
  delay_air_customs_functions.apply_async(kwargs={'air_customs_object':air_customs_rate, 'request':request,},queue = 'low')

  return {'id': air_customs_rate.id}

def get_create_object_params(request):
    return {
      'location_id':request.get('location_id'),
      'trade_type' : request.get('trade_type'),
      'container_size' : request.get('container_size'),
      'container_type' : request.get('container_type'),
      'service_provider_id': request.get('service_provider_id'),
      'commodity' : request.get('commodity'),
      'importer_exporter_id' : request.get('importer_exporter_id')
    }

def create_audit(request, customs_rate_id):
  audit_data = {
      'customs_line_items': request.get('customs_line_items')
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