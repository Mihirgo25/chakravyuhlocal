from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from database.db_session import db
from datetime import datetime
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
    ## remove this during prodution for testing I am taking some constant value for performed_by_id
    request['performed_ by_id'] = '515a7d68-3527-422d-9fce-f63bec350d78'
    #########
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

  validate_freight_params(request)

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
    if request['rate_type']=='cogo_assured':
      if ('code' not in request['line_items'][0]):
            create_line_items_cogo_assured(request.get("line_items"),freight,request)
      else:
            create_validities_for_cogo_assured(request,freight_object)
    else:
      freight_object.validate_line_items(request.get('line_items'))
      freight_object.set_validities(request.get('validity_start').date(), request.get('validity_end').date(), request.get('line_items'), request.get('schedule_type'), False, request.get('payment_term'))
    freight_object.set_platform_prices()
    freight_object.set_is_best_price()
    freight_object.set_last_rate_available_date()

  freight_object.sourced_by_id = request.get("sourced_by_id")
  freight_object.procured_by_id = request.get("procured_by_id")
  
  freight_object.validate_before_save()

  try:
    freight_object.save()
  except:
      raise HTTPException(status_code=500, detail='rate did not update')
  
  freight_object.create_fcl_freight_free_days(new_free_days, request.get('performed_by_id'), request.get('sourced_by_id'), request.get('procured_by_id'))

  freight_object.update_special_attributes()

  freight_object.update_platform_prices_for_other_service_providers()

  freight_object.create_trade_requirement_rate_mapping(request.get('procured_by_id'), request['performed_by_id'])

  update_multiple_service_objects.apply_async(kwargs={'object':freight_object},queue='critical')

  create_audit(request, freight_object.id)

  current_validities = freight_object.validities
  adjust_dynamic_pricing(request, freight_object, current_validities)

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
        'service_provider_id': freight.service_provider_id
    }
    if rate_obj["mode"] == 'manual' and not request.get("is_extended"):
        extend_fcl_freight_rates.apply_async(kwargs={ 'rate': rate_obj }, queue='low')

    adjust_fcl_freight_dynamic_pricing.apply_async(kwargs={ 'new_rate': rate_obj, 'current_validities': current_validities }, queue='low')
def create_line_items_cogo_assured(validities,freight,request):
    line_items = []
    for validity in validities:
        validity_start = datetime.strptime(validity['validity_start'].split('T')[0], '%Y-%m-%d').date()
        validity_end = datetime.strptime(validity['validity_end'].split('T')[0], '%Y-%m-%d').date()
        updated_validity = {k: v for k, v in validity.items() if k not in ["validity_start", "validity_end"]}
        updated_validity["code"] = "BAS"
        updated_validity["unit"] = "per_container"
        line_items.append(updated_validity)
        freight.set_validities(
                    validity_start,
                    validity_end,
                    [updated_validity],
                    request.get("schedule_type"),
                    False,
                    request.get("payment_term"),
                 )
        request["line_items"] = line_items
def create_validities_for_cogo_assured(request,freight):
    for line_item in request['line_items']:
        print(line_item)
        validity_start = line_item.pop("validity_start")
        validity_end = line_item.pop("validity_end")
        freight.set_validities(
            validity_start,
            validity_end,
            [line_item],
            request.get("schedule_type"),
            False,
            request.get("payment_term"),
     )
 