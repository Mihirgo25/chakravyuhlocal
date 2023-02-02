from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
import json
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
import os
import time

def find_or_initialize(**kwargs):
  try:
    obj = FclFreightRate.get(**kwargs)
  except FclFreightRate.DoesNotExist:
    obj = FclFreightRate(**kwargs)
  return obj

def to_dict(obj):
    return obj

def create_audit(request, freight_id):

    request.validity_start = request.validity_start.isoformat()
    request.validity_end = request.validity_end.isoformat()

    request = to_dict(request)

    audit_data = {}
    audit_data['validity_start'] = request['validity_start']
    audit_data['validity_end'] = request['validity_end']
    audit_data['line_items'] = request['line_items']
    audit_data['weight_limit'] = request['weight_limit']
    audit_data['origin_local'] = request['origin_local']
    audit_data['destination_local'] = request['destination_local']

    FclFreightRateAudit.create(
        bulk_operation_id = request['bulk_operation_id'],
        rate_sheet_id = request['rate_sheet_id'],
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        procured_by_id = request['procured_by_id'],
        sourced_by_id = request['sourced_by_id'],
        data = audit_data,
        object_id = freight_id,
        object_type = 'FclFreightRate'
    )
    

def create_fcl_freight_rate_data(request):
  row = {
    'origin_port_id' : request.get("origin_port_id"),
    'origin_main_port_id' : request.get("origin_main_port_id"),
    'destination_port_id' : request["destination_port_id"],
    'destination_main_port_id' : request.get("destination_main_port_id"),
    'container_size' : request["container_size"],
    'container_type' : request["container_type"],
    'commodity' : request["commodity"],
    'shipping_line_id' : request["shipping_line_id"],
    'service_provider_id' : request["service_provider_id"],
    'importer_exporter_id' : request.get("importer_exporter_id"),
    'rate_not_available_entry' : False
  }

  freight = find_or_initialize(**row)
  freight.set_locations()
  freight.set_shipping_line()

  freight.weight_limit = to_dict(request["weight_limit"])
  if freight.origin_local:
    freight.origin_local.update(to_dict(request.get("origin_local")))
  else:
    freight.origin_local = to_dict(request.get("origin_local"))
    
  print(freight.origin_local)

  if freight.destination_local:
    freight.destination_local.update(to_dict(request["destination_local"]))
  else:
    freight.destination_local = to_dict(request["destination_local"])
  
  freight.validate_validity_object(request["validity_start"], request["validity_end"])

  freight.validate_line_items(to_dict(request.line_items))

  freight.set_validities(request["validity_start"], request["validity_end"], to_dict(request["line_items"]), request["schedule_type"], False, request["payment_term"])
  freight.set_platform_prices()
  freight.set_is_best_price()
  freight.set_last_rate_available_date()

  freight.validate_before_save()

  try:
    freight.save()
  except:
    raise HTTPException(status_code=499, detail='rate did not save')

  if not request.importer_exporter_id:
    freight.delete_rate_not_available_entry()
  
  create_audit(request, freight.id)

  freight.update_special_attributes() #check this properly
  
  freight.update_local_references() #check this properly

  freight.update_platform_prices_for_other_service_providers()

  freight.create_trade_requirement_rate_mapping(request.procured_by_id, request.performed_by_id)

  create_sailing_schedule_port_pair(request)

  create_freight_trend_port_pair(request)

  # UpdateOrganization.delay(queue: 'critical').run!(id: self.service_provider_id, freight_rates_added: true) unless FclFreightRate.where(service_provider_id: self.service_provider_id, rate_not_available_entry: false).exists?

  return {"id": freight.id}
  # return {"id": 1}

def create_sailing_schedule_port_pair(request):
  port_pair_coverage_data = {
  'origin_port_id': request.origin_main_port_id if request.origin_main_port_id else request.origin_port_id,
  'destination_port_id': request.destination_main_port_id if request.destination_main_port_id else request.destination_port_id,
  'shipping_line_id': request.shipping_line_id
  }
  # CreateSailingSchedulePortPairCoverage.delay(queue: 'low').run!(port_pair_coverage_data) #call this private api

def create_freight_trend_port_pair(request):
  port_pair_data = {
      'origin_port_id': request.origin_port_id,
      'destination_port_id': request.destination_port_id
  }
  # CreateFreightTrendPortPair.delay(queue: 'low').run!(port_pair_data) #expose and call this api
