from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
import json
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
import requests

def find_or_initialize(**kwargs):
  try:
    obj = FclFreightRate.get(**kwargs)
  except FclFreightRate.DoesNotExist:
    obj = FclFreightRate(**kwargs)
  return obj

def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

def create_audit(request):
    audit_data = {k: request for k in ('validity_start', 'validity_end', 'line_items', 'weight_limit', 'origin_local', 'destination_local')}

    print(dict(audit_data))

    audit_data.update({
        'bulk_operation_id': request.bulk_operation_id,
        'rate_sheet_id': request.rate_sheet_id,
        'action_name': 'create',
        'performed_by_id': request.performed_by_id,
        'procured_by_id': request.procured_by_id,
        'sourced_by_id': request.sourced_by_id,
        'data': audit_data
    })

    FclFreightRateAudit.create(audit_data)
    

def create_fcl_freight_rate(request):
  row = {
    'origin_port_id' : request.origin_port_id,
    'origin_main_port_id' : request.origin_main_port_id,
    'destination_port_id' : request.destination_port_id,
    'destination_main_port_id' : request.destination_main_port_id,
    'container_size' : request.container_size,
    'container_type' : request.container_type,
    'commodity' : request.commodity,
    'shipping_line_id' : request.shipping_line_id,
    'service_provider_id' : request.service_provider_id,
    'importer_exporter_id' : request.importer_exporter_id,
    'rate_not_available_entry' : False
  }

  freight = find_or_initialize(**row)

  # print(request.weight_limit)
  # print(dict(request.weight_limit))

  # freight.weight_limit = to_dict(request.weight_limit)

  # if freight.origin_local:
  #   freight.origin_local.update(to_dict(request.origin_local))
  # else:
  #   freight.origin_local = to_dict(request.origin_local)

  # if freight.destination_local:
  #   freight.destination_local.update(to_dict(request.destination_local))
  # else:
  #   freight.destination_local = to_dict(request.destination_local)
  
  freight.validate_validity_object(request.validity_start, request.validity_end)

  # origin_port = requests.get("https://api-nirvana1.dev.cogoport.io/location/list_locations?filters%5Bid%5D=" + str(request.origin_port_id)).json()['list'][0]
  # destination_port = requests.get("https://api-nirvana1.dev.cogoport.io/location/list_locations?filters%5Bid%5D=" + str(request.destination_port_id)).json()['list'][0]
  # origin_main_port = requests.get("https://api-nirvana1.dev.cogoport.io/location/list_locations?filters%5Bid%5D=" + str(request.origin_main_port_id)).json()['list'][0]
  # destination_main_port = requests.get("https://api-nirvana1.dev.cogoport.io/location/list_locations?filters%5Bid%5D=" + str(request.destination_main_port_id)).json()['list'][0]

  # freight.validate_line_items(to_dict(request.line_items))

  # freight.set_validities(request.validity_start, request.validity_end, to_dict(request.line_items), request.schedule_type, False, request.payment_term)
  # freight.set_platform_prices()
  # freight.set_is_best_price()
  # freight.set_last_rate_available_date()

  # try:
  #   freight.save()
  # except:
  #   raise HTTPException(status_code=499, detail='rate did not save')

  # if not request.importer_exporter_id:
  #   freight.delete_rate_not_available_entry()
  
  # freight.audits.create!(create_audit) 
  # create_audit(request) # convert obj to dict

  # freight.update_special_attributes()
  


  return {"id": freight.id}
  # return {"id": 1}