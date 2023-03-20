from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
import json
from database.db_session import db
from playhouse.shortcuts import model_to_dict

def create_audit(request, freight_id):
    audit_data = {}
    audit_data['validity_start'] = request['validity_start'].isoformat()
    audit_data['validity_end'] = request['validity_end'].isoformat()
    audit_data['line_items'] = request['line_items']
    audit_data['weight_limit'] = request['weight_limit']
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

  freight_object = FclFreightRate.get_by_id(request['id'])

  for k,v in request.items():
    if k in ['weight_limit']:
      setattr(freight_object, k, v)

  origin_local = {k:v for k, v in request.get("origin_local", {}).items() if k not in ["detention", "demurrage"]}
  destination_local = {k:v for k, v in request.get("destination_local", {}).items() if k not in ["detention", "demurrage"]}

  if request.get("origin_local"):
    freight_object.origin_local = origin_local

  if request.get("destination_local"):
    freight_object.destination_local = destination_local

  freight_object.origin_detention = request.get("origin_local", {}).get("detention",{})
  freight_object.origin_demurrage = request.get("origin_local", {}).get("demurrage",{})
  freight_object.destination_detention = request.get("destination_local", {}).get("detention",{})
  freight_object.destination_demurrage = request.get("destination_local", {}).get("demurrage",{})

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
      raise HTTPException(status_code=499, detail='rate did not update')

  freight_object.update_special_attributes()

  freight_object.update_platform_prices_for_other_service_providers()

  freight_object.create_trade_requirement_rate_mapping(request['procured_by_id'], request['performed_by_id'])

  create_audit(request, freight_object.id)

  return {
    'id': freight_object.id
  }