from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from celery_worker import celery

def create_audit(request, freight_id):
    audit_data = {}
    audit_data['validity_start'] = request['validity_start'].isoformat()
    audit_data['validity_end'] = request['validity_end'].isoformat()
    audit_data['line_items'] = request['line_items']
    audit_data['weight_limit'] = request['weight_limit']
    audit_data['origin_local'] = request.get('origin_local')
    audit_data['destination_local'] = request.get('destination_local')

    FclFreightRateAudit.create(
        bulk_operation_id = request.get('bulk_operation_id'),
        action_name = 'update',
        performed_by_id = request['performed_by_id'],
        procured_by_id = request['procured_by_id'],
        sourced_by_id = request['sourced_by_id'],
        data = audit_data,
        object_id = freight_id,
        object_type = 'FclFreightRate'
    )

def validate_freight_params(request):
  if request.get('validity_start') or request.get('validity_end') or request.get('line_items'):
    keys = ['validity_start', 'validity_end', 'line_items']
    for key in keys:
      if not request.get(key):
       HTTPException(status_code=499, detail="{key} is blank")

def update_fcl_freight_rate_data(request):
  validate_freight_params(request)

  freight_object = FclFreightRate.get_by_id(request['id'])
  update_weight_limit = {key: value for key, value in request.items() if key in ['weight_limit']}
  freight_object.update(**update_weight_limit)

  freight_object.origin_local = {**freight_object.origin_local.as_dict(), **request.get('origin_local', {})}

  freight_object.destination_local = {**freight_object.destination_local.as_dict(), **request.get('destination_local', {})}

  if request.get('validity_start'):
    update_freight_validities(freight_object)

  try:
    freight_object.save()
  except:
    raise HTTPException(status_code=499, detail='rate did not update')

  freight_object.update_special_attributes()

  freight_object.update_platform_prices_for_other_service_providers()

  freight_object.create_trade_requirement_rate_mapping(request['procured_by_id'], request['performed_by_id'])

  create_audit(request, freight_object.id)

  return {
    'id': freight_object.id,
  }

def update_freight_validities(freight, request):
  freight.validate_validity_object(request['validity_start'], request['validity_end'])
  freight.validate_line_items(request['line_items'])

  freight.set_validities(request.validity_start, request.validity_end, request.line_items, request.schedule_type, False, request.payment_term)

  freight.set_platform_prices()
  freight.set_is_best_price()
  freight.set_last_rate_available_date()