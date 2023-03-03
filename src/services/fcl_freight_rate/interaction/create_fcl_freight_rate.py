from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
import json
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
import os
import time
from params import LocalData
from rails_client import client
from services.fcl_freight_rate.helpers.find_or_initialize import find_or_initialize


def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

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
        rate_sheet_id = request.get('rate_sheet_id'),
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
    'destination_port_id' : request.get("destination_port_id"),
    'destination_main_port_id' : request.get("destination_main_port_id"),
    'container_size' : request.get("container_size"),
    'container_type' : request.get("container_type"),
    'commodity' : request.get("commodity"),
    'shipping_line_id' : request.get("shipping_line_id"),
    'service_provider_id' : request.get("service_provider_id"),
    'importer_exporter_id' : request.get("importer_exporter_id"),
    'rate_not_available_entry' : False
  }

  freight = find_or_initialize(FclFreightRate,**row)
  freight.set_locations()
  freight.set_shipping_line()
  freight.set_origin_location_ids()
  freight.set_destination_location_ids()
  freight.validate_service_provider()
  freight.validate_importer_exporter()

  freight.weight_limit = to_dict(request.get("weight_limit"))

  if freight.origin_local and request.get("origin_local"):
    freight.origin_local.update(to_dict(request.get("origin_local")))
  elif request.get("origin_local"):
    freight.origin_local = to_dict(request.get("origin_local"))
  else:
     freight.origin_local= {
      "line_items":[],
      "detention":  None,
      "demurrage": None,
      "plugin":  None
    }

  if freight.destination_local and request.get("destination_local"):
    freight.destination_local.update(to_dict(request.get("destination_local")))
  elif request.get("destination_local"):
    freight.destination_local = to_dict(request.get("destination_local"))
  else:
    freight.destination_local= {
      "line_items":[],
      "detention":  None,
      "demurrage": None,
      "plugin":  None
    }

  freight.validate_validity_object(request["validity_start"], request["validity_end"])

  freight.validate_line_items(to_dict(request.get("line_items")))

  freight.set_validities(request["validity_start"].date(), request["validity_end"].date(), to_dict(request["line_items"]), request["schedule_type"], False, request["payment_term"])

  freight.set_platform_prices()
  freight.set_is_best_price()
  freight.set_last_rate_available_date()
  freight.validate_before_save()

  try:
    freight.save()
  except Exception as e:
    print("Exception in saving freight rate", e)
    raise HTTPException(status_code=499, detail='rate did not save')

  if not request.get('importer_exporter_id'):
    freight.delete_rate_not_available_entry()

  create_audit(request, freight.id)

  freight.update_special_attributes()
  
  freight.update_local_references()

  freight.update_platform_prices_for_other_service_providers()

  # freight.create_trade_requirement_rate_mapping(request['procured_by_id'], request['performed_by_id'])

  # create_sailing_schedule_port_pair(request) # call this ruby api

  # create_freight_trend_port_pair(request)

  # if not FclFreightRate.where(service_provider_id=request["service_provider_id"], rate_not_available_entry=False).exists():
  #   client.ruby.update_organization({'id':request.get("service_provider_id"), "freight_rates_added":True})

  # if request.get(fcl_freight_rate_request_id):
  #   DeleteFclFreightRateRequest.run!(fcl_freight_rate_request_ids=[request.fcl_freight_rate_request_id])

  return {"id": freight.id}
  # return {"id": 1}

def create_sailing_schedule_port_pair(request):
  port_pair_coverage_data = {
  'origin_port_id': request.origin_main_port_id if request.origin_main_port_id else request.origin_port_id,
  'destination_port_id': request.destination_main_port_id if request.destination_main_port_id else request.destination_port_id,
  'shipping_line_id': request.shipping_line_id
  }
  # in delay private api call
  client.ruby.create_sailing_schedule_port_pair_coverage(port_pair_coverage_data)

def create_freight_trend_port_pair(request):
  port_pair_data = {
      'origin_port_id': request.origin_port_id,
      'destination_port_id': request.destination_port_id
  }
  # in delay(queue:low) private api call and expose
  client.ruby.create_freight_trend_port_pair(port_pair_data)