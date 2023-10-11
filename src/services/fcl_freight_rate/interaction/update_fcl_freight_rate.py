from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.fcl_freight_rate.helpers.get_normalized_line_items import get_normalized_line_items
from database.db_session import db
from datetime import datetime
from libs.get_multiple_service_objects import get_multiple_service_objects
from configs.global_constants import DEFAULT_SERVICE_PROVIDER_ID

def create_audit(request, freight_id):
    validity_start = request.get('validity_start')
    validity_end = request.get('validity_end')
    audit_data = {}
    audit_data['validity_start'] = validity_start.isoformat() if validity_start else datetime.now().isoformat()
    audit_data['validity_end'] = validity_end.isoformat() if validity_end else datetime.now().isoformat()
    audit_data['line_items'] = request.get('line_items')
    audit_data['weight_limit'] = request.get('weight_limit')
    audit_data['origin_local'] = request.get('origin_local')
    audit_data['destination_local'] = request.get('destination_local')
    audit_data['is_extended'] = request.get("is_extended")
    audit_data['sourced_by_id'] = request.get("sourced_by_id")
    audit_data['procured_by_id'] = request.get("procured_by_id")
    audit_data['payment_term'] = request.get("payment_term")
    audit_data['schedule_type'] = request.get("schedule_type")

    FclFreightRateAudit.create(
        bulk_operation_id = request.get('bulk_operation_id'),
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        data = audit_data,
        object_id = freight_id,
        object_type = 'FclFreightRate',
        source = request.get("source"),
        performed_by_type = request.get("performed_by_type") or "agent"
    )

def update_fcl_freight_rate_data(request):
    with db.atomic():
        return execute_transaction_code(request)


def validate_freight_params(request):
  if request.get('validity_start') or request.get('validity_end') or request.get('line_items'):
    keys = ['validity_start', 'validity_end', 'line_items']
    for key in keys:
      if not request.get(key):
        HTTPException(status_code=400, detail="{key} is blank")

def execute_transaction_code(request):
  from celery_worker import update_multiple_service_objects
  from services.fcl_freight_rate.fcl_celery_worker import update_fcl_freight_rate_job_on_rate_addition_delay

  validate_freight_params(request)
  
  request['line_items'] = get_normalized_line_items(request['line_items'])

  freight_object = FclFreightRate.select().where(FclFreightRate.id == request["id"]).first()

  if not freight_object:
    raise HTTPException(status_code=400, detail="rate does not exist")
  
  freight_object.set_locations()

  for k,v in request.items():
    if k in ['weight_limit']:
      setattr(freight_object, k, v)
  
  new_free_days = {}

  new_free_days['origin_detention'] = request.get("origin_local", {}).get("detention", {})
  new_free_days['origin_demurrage'] = request.get("origin_local", {}).get("demurrage", {})
  new_free_days['destination_detention'] = request.get("destination_local", {}).get("detention", {})
  new_free_days['destination_demurrage'] = request.get("destination_local", {}).get("demurrage", {})

  if request.get("origin_local") and "line_items" in request["origin_local"]:
    freight_object.origin_local = {
        "line_items": get_normalized_line_items(request["origin_local"]["line_items"])
    }
  else:
    freight_object.origin_local = { "line_items": [] }
  if request.get("destination_local") and "line_items" in request["destination_local"]:
    freight_object.destination_local = {
        "line_items": get_normalized_line_items(request["destination_local"]["line_items"])
    }
  else:
    freight_object.destination_local = { "line_items": [] }

  if request.get('validity_start'):
    freight_object.validate_validity_object(request.get('validity_start'), request.get('validity_end'))
    
    if request['rate_type'] != "cogo_assured":
      freight_object.validate_line_items(request.get('line_items'))
      freight_object.set_validities(request.get('validity_start').date(), request.get('validity_end').date(), request.get('line_items'), request.get('schedule_type'), False, request.get('payment_term'))
    else:
      freight_object.set_validities_for_cogo_assured_rates(request['validities'])

    freight_object.set_platform_prices(request['rate_type'])
    freight_object.set_is_best_price()
    freight_object.set_last_rate_available_date()

  freight_object.sourced_by_id = request.get("sourced_by_id")
  freight_object.procured_by_id = request.get("procured_by_id")
  freight_object.rate_not_available_entry = request.get("rate_not_available_entry")
  
  freight_object.validate_before_save()

  try:
    freight_object.save()
  except:
      raise HTTPException(status_code=500, detail='rate did not update')
  
  freight_object.create_fcl_freight_free_days(new_free_days, request.get('performed_by_id'), request.get('sourced_by_id'), request.get('procured_by_id'))

  freight_object.update_special_attributes()

  freight_object.update_platform_prices_for_other_service_providers()

  freight_object.create_trade_requirement_rate_mapping(request.get('procured_by_id'), request['performed_by_id'])
  
  get_multiple_service_objects(freight_object, is_new_rate=False)

  create_audit(request, freight_object.id)

  current_validities = freight_object.validities
  adjust_dynamic_pricing(request, freight_object, current_validities)
  
  send_stats(request,freight_object)

  if str(freight_object.service_provider_id) != DEFAULT_SERVICE_PROVIDER_ID:
     update_fcl_freight_rate_job_on_rate_addition_delay.apply_async(kwargs={'request': request, "id": freight_object.id},queue='fcl_freight_rate')

  return {
    'id': freight_object.id
  }

def adjust_dynamic_pricing(request, freight: FclFreightRate, current_validities):
    from celery_worker import extend_fcl_freight_rates, adjust_fcl_freight_dynamic_pricing
    rate_obj = request | { 
        'origin_port_id': freight.origin_port_id,
        'destination_port_id': freight.destination_port_id,
        'mode': 'manual',
        'schedule_type': request.get('schedule_type'),
        'payment_term': request.get('payment_term'),
        'line_items': request.get('line_items') or [],
        'origin_location_ids': freight.origin_location_ids,
        'destination_location_ids': freight.destination_location_ids,
        'id': freight.id,
        'origin_country_id': freight.origin_country_id,
        'destination_country_id': freight.destination_country_id,
        'origin_trade_id': freight.origin_trade_id,
        'destination_trade_id': freight.destination_trade_id,
        'validities': freight.validities,
        'shipping_line_id': freight.shipping_line_id,
        'commodity': freight.commodity,
        'container_size': freight.container_size,
        'container_type': freight.container_type,
        'service_provider_id': freight.service_provider_id,
        'rate_type': freight.rate_type,
        'extend_rates_for_existing_system_rates': True
    }
    if rate_obj["mode"] == 'manual' and not request.get("is_extended") and rate_obj['rate_type'] == 'market_place':
        extend_fcl_freight_rates.apply_async(kwargs={ 'rate': rate_obj }, queue='low')

    adjust_fcl_freight_dynamic_pricing.apply_async(kwargs={ 'new_rate': rate_obj, 'current_validities': current_validities }, queue='low')
    
  
def send_stats(request,freight):
    from services.bramhastra.celery import send_fcl_rate_stats_in_delay
    send_fcl_rate_stats_in_delay.apply_async(kwargs = {'action':'update','request':request,'freight':freight},queue = 'statistics')
