from services.fcl_freight_rate.models.fcl_freight_rate_locals import FclFreightRateLocal
import json
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
# import requests 

def find_or_initialize(**kwargs):
  try:
    obj = FclFreightRateLocal.get(**kwargs)
  except FclFreightRateLocal.DoesNotExist:
    obj = FclFreightRateLocal(**kwargs)
  return obj

def to_dict(obj):
    return json.loads(json.dumps(obj, default=lambda o: o.__dict__))

def create_fcl_freight_rate_local_data(request):

  if not request.source:
    request.source = 'rms_upload'

  row = {
    'port_id' : request.port_id,
    'trade_type' : request.trade_type,
    'main_port_id' : request.main_port_id,
    'container_size' : request.container_size,
    'container_type' : request.container_type,
    'commodity' : request.commodity,
    'shipping_line_id' : request.shipping_line_id,
    'service_provider_id' : request.service_provider_id,
  }

  fcl_freight_local = find_or_initialize(**row)

  request = to_dict(request)

  fcl_freight_local.rate_not_available_entry = False

  fcl_freight_local.selected_suggested_rate_id = request['selected_suggested_rate_id']

  # if request['data']['line_items']:
  #   if fcl_freight_local.data:
  #     fcl_freight_local.data.update({key : value for key, value in request['data'].items() if key == 'line_items'})
  #   else:
  #     fcl_freight_local.data = {key : value for key, value in request['data'].items() if key == 'line_items'}

  # print(fcl_freight_local.data)

  if request['data']['detention']:
    detention_obj = {}
    detention_obj['location_id'] = request['port_id']
    detention_obj['free_day_type'] = 'detention'
    detention_obj['specificity_type'] = 'shipping_line'
    detention_obj['previous_days_applicable'] = False

    detention_obj.update({key: value for key, value in request['data']['detention'].items() if key in ('free_limit', 'slabs', 'remarks')})
    detention_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id')})

    # detention = #API call to create detention
    # fcl_freight_local.detention_id = detention['id']

  if request['data']['demurrage']:
    demurrage_obj = {}
    demurrage_obj['location_id'] = request['port_id']
    demurrage_obj['free_day_type'] = 'demurrage'
    demurrage_obj['specificity_type'] = 'shipping_line'
    demurrage_obj['previous_days_applicable'] = False

    demurrage_obj.update({key: value for key, value in request['data']['demurrage'].items() if key in ('free_limit', 'slabs', 'remarks')})
    demurrage_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id')})

    # demurrage = #API call to create demurrage
    # fcl_freight_local.demurrage_id = demurrage['id']

  if request['data']['plugin']:
    plugin_obj = {}
    plugin_obj['location_id'] = request['port_id']
    plugin_obj['free_day_type'] = 'plugin'
    plugin_obj['specificity_type'] = 'shipping_line'
    plugin_obj['previous_days_applicable'] = False

    plugin_obj.update({key: value for key, value in request['data']['plugin'].items() if key in ('free_limit', 'slabs', 'remarks')})
    plugin_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id')})

    # plugin = #API call to create plugin
    # fcl_freight_local.plugin_id = plugin['id']

  try:
    fcl_freight_local.save()
  except:
    raise HTTPException(status_code=499, detail='fcl freight rate local did not save')

  # fcl_freight_local.update_special_attributes

  # fcl_freight_local.update_freight_objects

  # fcl_freight_local.audits.create!(get_audit_params)

  # create_organization_serviceable_port

  return {"id": fcl_freight_local.id}


def create_organization_serviceable_port(request):
  params = {
    'performed_by_id': request['performed_by_id'],
    'organization_id': request['service_provider_id'],
    'port_id': request['port_id'],
    'trade_type': request['trade_type']
  }
  # CreateOrganizationServiceablePort.delay(queue: 'low').run!(params)

  