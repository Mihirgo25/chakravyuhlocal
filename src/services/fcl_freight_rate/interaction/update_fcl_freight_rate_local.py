from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
import json
from fastapi import FastAPI, HTTPException
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import create_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_free_day import update_fcl_freight_rate_free_day
from database.db_session import db
# import requests 


def update_fcl_freight_rate_local_data(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except:
            transaction.rollback()
            return "update failed"

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

def update_freight_objects(fcl_freight_local):
    location_key = 'origin' if fcl_freight_local.trade_type == 'export' else 'destination'

    t = FclFreightRate.get(
      FclFreightRate.container_size == fcl_freight_local.container_size,
      FclFreightRate.container_type == fcl_freight_local.container_type,
      FclFreightRate.shipping_line_id == fcl_freight_local.shipping_line_id,
      FclFreightRate.service_provider_id == fcl_freight_local.service_provider_id,
      eval(f"FclFreightRate.{location_key}_port_id") == fcl_freight_local.port_id,
      eval(f"FclFreightRate.{location_key}_main_port_id") == fcl_freight_local.main_port_id
    )


    if fcl_freight_local.commodity:
      t = t.where(FclFreightRate.commodity == fcl_freight_local.commodity)

    t.where(f"FclFreightRate.{location_key}_local_id" == None).update({f"FclFreightRate.{location_key}_local_id": fcl_freight_local.id}).execute()

def execute_transaction_code(request):

  fcl_freight_local = FclFreightRateLocal.get_by_id(request['id'])

  fcl_freight_local.selected_suggested_rate_id = request.get('selected_suggested_rate_id')

  if request.get('data') and request['data'].get('line_items'):
    # if fcl_freight_local.data:
    #   fcl_freight_local.data.update({key : value for key, value in request['data'].items() if key == 'line_items'})
    # else:
    #   fcl_freight_local.data = {key : value for key, value in request['data'].items() if key == 'line_items'}
      fcl_freight_local.data = json.loads(fcl_freight_local.data) | ({'line_items':request['line_items']})

  if request.get('data') and request['data'].get('detention'):

    if fcl_freight_local.detention_id:
      update_obj = {}
      update_obj['id'] = fcl_freight_local.detention_id
      update_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'procured_by_id', 'sourced_by_id')})
      update_obj.update({key: value for key, value in request['data']['detention'].items() if key in ('free_limit', 'slabs', 'remarks')})

      update_fcl_freight_rate_free_day(update_obj)

    else:
      fcl_freight_local.data['detention'] = None
      detention_obj = {}
      detention_obj['location_id'] = request.get('port_id')
      detention_obj['free_day_type'] = 'detention'
      detention_obj['specificity_type'] = 'shipping_line'
      detention_obj['previous_days_applicable'] = False

      detention_obj.update({key: value for key, value in request['data']['detention'].items() if key in ('free_limit', 'slabs', 'remarks')})

      detention_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id')})

      detention_obj.update({
        'trade_type': fcl_freight_local.trade_type,
        'container_type': fcl_freight_local.container_type,
        'container_size': fcl_freight_local.container_size,
        'shipping_line_id': fcl_freight_local.shipping_line_id,
        'service_provider_id': fcl_freight_local.service_provider_id
      })

      detention = create_fcl_freight_rate_free_day(detention_obj)
      fcl_freight_local.detention_id = detention['id']

  if request['data'].get('demurrage'):

    if fcl_freight_local.demurrage_id:
      update_obj = {}
      update_obj['id'] = fcl_freight_local.demurrage_id
      update_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'procured_by_id', 'sourced_by_id')})
      update_obj.update({key: value for key, value in request['data']['demurrage'].items() if key in ('free_limit', 'slabs', 'remarks')})
      
      update_fcl_freight_rate_free_day(update_obj)

    else:
      fcl_freight_local.data['demurrage'] = None
      demurrage_obj = {}
      demurrage_obj['location_id'] = request.get('port_id')
      demurrage_obj['free_day_type'] = 'demurrage'
      demurrage_obj['specificity_type'] = 'shipping_line'
      demurrage_obj['previous_days_applicable'] = False

      demurrage_obj.update({key: value for key, value in request['data']['demurrage'].items() if key in ('free_limit', 'slabs', 'remarks')})

      demurrage_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id')})

      demurrage_obj.update({
        'trade_type': fcl_freight_local.trade_type,
        'container_type': fcl_freight_local.container_type,
        'container_size': fcl_freight_local.container_size,
        'shipping_line_id': fcl_freight_local.shipping_line_id,
        'service_provider_id': fcl_freight_local.service_provider_id
      })
      
      demurrage = create_fcl_freight_rate_free_day(demurrage_obj)
      fcl_freight_local.demurrage_id = demurrage['id']

  if request['data'].get('plugin'):

    if fcl_freight_local.plugin_id:
      update_obj = {}
      update_obj['id'] = fcl_freight_local.plugin_id
      update_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'procured_by_id', 'sourced_by_id')})
      update_obj.update({key: value for key, value in request['data']['plugin'].items() if key in ('free_limit', 'slabs', 'remarks')})
      
      update_fcl_freight_rate_free_day(update_obj)

    else:
      fcl_freight_local.data['plugin'] = None
      plugin_obj = {}
      plugin_obj['location_id'] = request.get('port_id')
      plugin_obj['free_day_type'] = 'plugin'
      plugin_obj['specificity_type'] = 'shipping_line'
      plugin_obj['previous_days_applicable'] = False

      plugin_obj.update({key: value for key, value in request['data']['plugin'].items() if key in ('free_limit', 'slabs', 'remarks')})

      plugin_obj.update({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id')})

      plugin_obj.update({
        'trade_type': fcl_freight_local.trade_type,
        'container_type': fcl_freight_local.container_type,
        'container_size': fcl_freight_local.container_size,
        'shipping_line_id': fcl_freight_local.shipping_line_id,
        'service_provider_id': fcl_freight_local.service_provider_id
      })
      
      plugin = create_fcl_freight_rate_free_day(plugin_obj)
      fcl_freight_local.plugin_id = plugin['id']

  fcl_freight_local.before_save()

  try:
    fcl_freight_local.save()
  except:
    raise HTTPException(status_code=499, detail='fcl freight rate local did not save')

  fcl_freight_local.update_special_attributes()

  create_audit(request, fcl_freight_local.id)

  return {"id": fcl_freight_local.id}
  