from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from database.db_session import db

def create_audit(request, freight_id):
    audit_data = {}
    audit_data['validity_start'] = request.get('validity_start').isoformat()
    audit_data['validity_end'] = request.get('validity_end').isoformat()
    audit_data['line_items'] = request.get('line_items')
    audit_data['weight_limit'] = request.get('weight_limit')
    audit_data['origin_local'] = request.get('origin_local')
    audit_data['destination_local'] = request.get('destination_local')
    audit_data['is_extended'] = request.get("is_extended")

    FclFreightRateAudit.create(
        bulk_operation_id = request.get('bulk_operation_id'),
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        data = audit_data,
        object_id = freight_id,
        object_type = 'FclFreightRate',
        source = request.get("source")
    )

def update_fcl_freight_rate_data(request):
    with db.atomic() as transaction:
          try:
              return execute_transaction_code(request)
          except Exception as e:
              transaction.rollback()
              return e

def validate_freight_params(request):
  if request.get('validity_start') or request.get('validity_end') or request.get('line_items'):
    keys = ['validity_start', 'validity_end', 'line_items']
    for key in keys:
      if not request.get(key):
        HTTPException(status_code=499, detail="{key} is blank")

def execute_transaction_code(request):
  validate_freight_params(request)

  freight_object = FclFreightRate.select().where(FclFreightRate.id == request["id"]).first()

  if not freight_object:
    raise HTTPException(status_code=499, detail="rate does not exist")
  
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
        "line_items": request["origin_local"]["line_items"]
    }
  else:
    freight_object.origin_local = { "line_items": [] }
  if request.get("destination_local") and "line_items" in request["destination_local"]:
    freight_object.destination_local = {
        "line_items": request["destination_local"]["line_items"]
    }
  else:
    freight_object.destination_local = { "line_items": [] }

  if request.get('validity_start'):
    freight_object.validate_validity_object(request.get('validity_start'), request.get('validity_end'))
    freight_object.validate_line_items(request.get('line_items'))
    freight_object.set_validities(request.get('validity_start').date(), request.get('validity_end').date(), request.get('line_items'), request.get('schedule_type'), False, request.get('payment_term'))
    freight_object.set_platform_prices()
    freight_object.set_is_best_price()
    freight_object.set_last_rate_available_date()
  
  freight_object.validate_before_save()

  try:
    freight_object.save()
  except:
      raise HTTPException(status_code=500, detail='rate did not update')
  
  freight_object.create_fcl_freight_free_days(new_free_days, request['performed_by_id'], request['sourced_by_id'], request['procured_by_id'])

  freight_object.update_special_attributes()

  freight_object.update_platform_prices_for_other_service_providers()

  freight_object.create_trade_requirement_rate_mapping(request['procured_by_id'], request['performed_by_id'])

  create_audit(request, freight_object.id)

  return {
    'id': freight_object.id
  }