from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import create_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_free_day import update_fcl_freight_rate_free_day
from services.fcl_freight_rate.helpers.get_normalized_line_items import get_normalized_line_items
from database.db_session import db
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from fastapi import HTTPException
from configs.env import  DEFAULT_USER_ID


def update_fcl_freight_rate_local(request):
    object_type = 'Fcl_Freight_Rate_Local' 
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
    db.execute_sql(query)
    validate_request(request)
    with db.atomic():
      return execute_transaction_code(request)

def validate_request(request):
    is_cogo_assured = request.get('rate_type') == 'cogo_assured'
    if not request.get('procured_by_id'):
      if is_cogo_assured:
        request['procured_by_id'] = request.get('performed_by_id')
      else:
        raise HTTPException(status_code=400, detail="Procured by id  is  required")
    
    if not request.get('sourced_by_id'):
      if is_cogo_assured:
        request['sourced_by_id'] = DEFAULT_USER_ID
      else:
        raise HTTPException(status_code=400, detail="Sourced by id  is required")
    


def create_audit(request, fcl_freight_local_id):
  
    audit_data = {}
    audit_data['data'] = request.get('data')
    audit_data['selected_suggested_rate_id'] = request.get('selected_suggested_rate_id')

    FclServiceAudit.create(
        rate_sheet_id = request.get('rate_sheet_id'),
        action_name = 'create',
        performed_by_id = request.get('performed_by_id'),
        data = audit_data,
        object_id = fcl_freight_local_id,
        object_type = 'FclFreightRateLocal'
    )

def execute_transaction_code(request):
  from celery_worker import update_multiple_service_objects

  fcl_freight_local = FclFreightRateLocal.get_by_id(request['id'])

  fcl_freight_local.selected_suggested_rate_id = request.get('selected_suggested_rate_id')

  if request.get('data') and request['data'].get('line_items'):
      fcl_freight_local.data = fcl_freight_local.data | {'line_items':get_normalized_line_items(request['data']['line_items'])}

  if request.get('data') and request['data'].get('detention'):
    if fcl_freight_local.detention_id:
      update_obj = {}
      update_obj['id'] = fcl_freight_local.detention_id
      update_obj = update_obj | ({key: value for key, value in request.items() if key in ('performed_by_id', 'procured_by_id', 'sourced_by_id')})
      update_obj = update_obj | ({key: value for key, value in request['data'].get('detention',{}).items() if key in ('free_limit', 'slabs', 'remarks')})

      update_fcl_freight_rate_free_day(update_obj)

    else:
      fcl_freight_local.data['detention'] = None
      detention_obj = {}
      detention_obj['location_id'] = fcl_freight_local.port_id
      detention_obj['free_days_type'] = 'detention'
      detention_obj['specificity_type'] = 'shipping_line'
      detention_obj['previous_days_applicable'] = False

      detention_obj = detention_obj | ({key: value for key, value in request['data'].get('detention',{}).items() if key in ('free_limit', 'slabs', 'remarks')})
      detention_obj = detention_obj | ({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id')})

      detention_obj = detention_obj | ({
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
      update_obj = update_obj | ({key: value for key, value in request.items() if key in ('performed_by_id', 'procured_by_id', 'sourced_by_id')})
      update_obj = update_obj | ({key: value for key, value in request['data'].get('demurrage',{}).items() if key in ('free_limit', 'slabs', 'remarks')})
      
      update_fcl_freight_rate_free_day(update_obj)

    else:
      fcl_freight_local.data['demurrage'] = None
      demurrage_obj = {}
      demurrage_obj['location_id'] = fcl_freight_local.port_id
      demurrage_obj['free_days_type'] = 'demurrage'
      demurrage_obj['specificity_type'] = 'shipping_line'
      demurrage_obj['previous_days_applicable'] = False

      demurrage_obj = demurrage_obj | ({key: value for key, value in request['data'].get('demurrage',{}).items() if key in ('free_limit', 'slabs', 'remarks')})
      demurrage_obj = demurrage_obj | ({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id')})

      demurrage_obj = demurrage_obj | ({
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
      update_obj = update_obj | ({key: value for key, value in request.items() if key in ('performed_by_id', 'procured_by_id', 'sourced_by_id')})
      update_obj = update_obj | ({key: value for key, value in request['data'].get('plugin',{}).items() if key in ('free_limit', 'slabs', 'remarks')})
      
      update_fcl_freight_rate_free_day(update_obj)

    else:
      fcl_freight_local.data['plugin'] = None
      plugin_obj = {}
      plugin_obj['location_id'] = fcl_freight_local.port_id
      plugin_obj['free_days_type'] = 'plugin'
      plugin_obj['specificity_type'] = 'shipping_line'
      plugin_obj['previous_days_applicable'] = False

      plugin_obj = plugin_obj | ({key: value for key, value in request['data'].get('plugin',{}).items() if key in ('free_limit', 'slabs', 'remarks')})
      plugin_obj = plugin_obj | ({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id')})

      plugin_obj = plugin_obj | ({
        'trade_type': fcl_freight_local.trade_type,
        'container_type': fcl_freight_local.container_type,
        'container_size': fcl_freight_local.container_size,
        'shipping_line_id': fcl_freight_local.shipping_line_id,
        'service_provider_id': fcl_freight_local.service_provider_id
      })
      
      plugin = create_fcl_freight_rate_free_day(plugin_obj)
      fcl_freight_local.plugin_id = plugin['id']

  fcl_freight_local.sourced_by_id = request.get("sourced_by_id")
  fcl_freight_local.procured_by_id = request.get("procured_by_id")
  fcl_freight_local.rate_not_available_entry = request.get("rate_not_available_entry")

  fcl_freight_local.validate_before_save()

  try:
    fcl_freight_local.save()
  except:
    raise HTTPException(status_code=500, detail='fcl freight rate local did not save')

  fcl_freight_local.update_special_attributes()

  get_multiple_service_objects(fcl_freight_local)

  create_audit(request, fcl_freight_local.id)

  return {"id": fcl_freight_local.id}
  