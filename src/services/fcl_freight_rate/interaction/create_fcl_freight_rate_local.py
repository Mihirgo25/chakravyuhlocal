from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
import json
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import create_fcl_freight_rate_free_day
from database.db_session import db
from playhouse.shortcuts import model_to_dict
# import requests


def find_or_initialize(**kwargs):
  try:
    obj = FclFreightRateLocal.get(**kwargs)
  except FclFreightRateLocal.DoesNotExist:
    obj = FclFreightRateLocal(**kwargs)
  return obj

def create_audit(request, fcl_freight_local_id):

    audit_data = {}
    audit_data['data'] = request.get('data')
    audit_data['selected_suggested_rate_id'] = request.get('selected_suggested_rate_id')

    FclFreightRateAudit.create(
        rate_sheet_id = request.get('rate_sheet_id'),
        action_name = 'create',
        performed_by_id = request.get('performed_by_id'),
        procured_by_id = request.get('procured_by_id'),
        sourced_by_id = request.get('sourced_by_id'),
        data = audit_data,
        object_id = fcl_freight_local_id,
        object_type = 'FclFreightRateLocal'
    )

def create_fcl_freight_rate_local_data(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except:
            transaction.rollback()
            return "Creation Failed"

def execute_transaction_code(request):
    if not request.get('source'):
        request['source'] = 'rms_upload'

    row = {
        'port_id' : request.get('port_id'),
        'trade_type' : request.get('trade_type'),
        'main_port_id' : request.get('main_port_id'),
        'container_size' : request.get('container_size'),
        'container_type' : request.get('container_type'),
        'commodity' : request.get('commodity'),
        'shipping_line_id' : request.get('shipping_line_id'),
        'service_provider_id' : request.get('service_provider_id')
    }

    fcl_freight_local = find_or_initialize(**row)

    fcl_freight_local.rate_not_available_entry = False
    fcl_freight_local.selected_suggested_rate_id = request.get('selected_suggested_rate_id')
    fcl_freight_local.rate_sheet_id = request.get('rate_sheet_id')
    fcl_freight_local.source = request.get('source')
    fcl_freight_local.data = request.get('data')
    
    if request['data'].get('line_items'):
      # if fcl_freight_local.data:
      #   fcl_freight_local.data.update({key : value for key, value in request['data'].items() if key == 'line_items'})
      # else:
        fcl_freight_local.data = {key : value for key, value in request['data'].items() if key == 'line_items'}


    if request['data'].get('detention'):
        detention_obj = {}
        detention_obj['location_id'] = request['port_id']
        detention_obj['free_days_type'] = 'detention'
        detention_obj['specificity_type'] = 'shipping_line'
        detention_obj['previous_days_applicable'] = False

        detention_obj.update({key: value for key, value in request['data']['detention'].items() if key in ('free_limit', 'slabs', 'remarks')})
        detention_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id')})

        detention = create_fcl_freight_rate_free_day(detention_obj)

        fcl_freight_local.detention_id = detention['id'] #check

    if request['data'].get('demurrage'):
        demurrage_obj = {}
        demurrage_obj['location_id'] = request['port_id']
        demurrage_obj['free_days_type'] = 'demurrage'
        demurrage_obj['specificity_type'] = 'shipping_line'
        demurrage_obj['previous_days_applicable'] = False

        demurrage_obj.update({key: value for key, value in request['data']['demurrage'].items() if key in ('free_limit', 'slabs', 'remarks')})
        demurrage_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id')})

        demurrage = create_fcl_freight_rate_free_day(demurrage_obj)

        fcl_freight_local.demurrage_id = demurrage['id']

    if request['data'].get('plugin'):
        plugin_obj = {}
        plugin_obj['location_id'] = request['port_id']
        plugin_obj['free_days_type'] = 'plugin'
        plugin_obj['specificity_type'] = 'shipping_line'
        plugin_obj['previous_days_applicable'] = False

        plugin_obj.update({key: value for key, value in request['data']['plugin'].items() if key in ('free_limit', 'slabs', 'remarks')})
        plugin_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id')})

        plugin = create_fcl_freight_rate_free_day(plugin_obj)

        fcl_freight_local.plugin_id = plugin['id']
   
    fcl_freight_local.before_save()

    try:
      fcl_freight_local.save()
    except Exception as e:
      raise HTTPException(status_code=499, detail='fcl freight rate local did not save')
    
    fcl_freight_local.update_special_attributes()
    fcl_freight_local.update_freight_objects()
    fcl_freight_local.save()

    create_audit(request, fcl_freight_local.id)

    # create_organization_serviceable_port
    return {"id": fcl_freight_local.id}


def create_organization_serviceable_port(request):
    params = {
      'performed_by_id': request['performed_by_id'],
      'organization_id': request['service_provider_id'],
      'port_id': request['port_id'],
      'trade_type': request['trade_type']
    }
    # CreateOrganizationServiceablePort.delay(queue: 'low').run!(params) #api call

  