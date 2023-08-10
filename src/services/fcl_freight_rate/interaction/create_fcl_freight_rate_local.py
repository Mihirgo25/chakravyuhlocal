from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import create_fcl_freight_rate_free_day
from database.db_session import db
from services.fcl_freight_rate.helpers.get_normalized_line_items import get_normalized_line_items
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE, DEFAULT_SHIPPING_LINE_ID
from configs.env import DEFAULT_USER_ID


def create_audit(request, fcl_freight_local_id):
    audit_data = {}
    audit_data['data'] = request.get('data')
    audit_data['selected_suggested_rate_id'] = request.get('selected_suggested_rate_id')

    FclServiceAudit.create(
        rate_sheet_id = request.get('rate_sheet_id'),
        action_name = 'create',
        performed_by_id = request.get('performed_by_id'),
        data = audit_data,
        sourced_by_id = request.get('sourced_by_id'),
        procured_by_id = request.get('procured_by_id'),
        object_id = fcl_freight_local_id,
        source = request.get('source'),
        object_type = 'FclFreightRateLocal'
    )

def create_fcl_freight_rate_local(request):
    object_type = 'Fcl_Freight_Rate_Local'
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
    db.execute_sql(query)
    validate_request(request)
    with db.atomic():
        return execute_transaction_code(request)
    
def validate_request(request):
    if not request.get('shipping_line_id'):
      if(request.get('rate_type') == 'cogo_assured'):
        request['shipping_line_id'] = DEFAULT_SHIPPING_LINE_ID 
      else:
        raise HTTPException(status_code=400, detail="shipping line id is required")

    if not request.get('service_provider_id'):
      if(request.get('rate_type') == 'cogo_assured'):
        request['service_provider_id'] = DEFAULT_USER_ID
      else:
        raise HTTPException(status_code=400, detail="service provider id is required")
    
    if not request.get('sourced_by_id'):
      if(request.get('rate_type') == 'cogo_assured'):
        request['sourced_by_id'] = DEFAULT_USER_ID
      
    
    if not request.get('procured_by_id'):
      if(request.get('rate_type') == 'cogo_assured'):
        request['procured_by_id'] = DEFAULT_USER_ID
     
    

def execute_transaction_code(request):
    from celery_worker import fcl_freight_local_data_updation, create_country_wise_locals_in_delay
    if not request.get('source'):
        request['source'] = 'rms_upload'

    if request.get('country_id') and not request.get('port_id'):
        create_country_wise_locals_in_delay.apply_async(kwargs={"request":request},queue='low')
        return {"message":"Creating rates in delay"}

    elif not request.get('country_id') and not request.get('port_id'):
        raise HTTPException(status_code=400, detail='Please select port or country')

    row = {
        'port_id' : request.get('port_id'),
        'trade_type' : request.get('trade_type'),
        'main_port_id' : request.get('main_port_id'),
        'container_size' : request.get('container_size'),
        'container_type' : request.get('container_type'),
        'commodity' : request.get('commodity'),
        'shipping_line_id' : request.get('shipping_line_id'),
        'service_provider_id' : request.get('service_provider_id'),
        "rate_not_available_entry": request.get("rate_not_available_entry"),
    }

    fcl_freight_local = FclFreightRateLocal.select().where(
        FclFreightRateLocal.port_id == request.get('port_id'),
        FclFreightRateLocal.trade_type ==request.get('trade_type'),
        FclFreightRateLocal.main_port_id == request.get('main_port_id'),
        FclFreightRateLocal.container_size== request.get('container_size'),
        FclFreightRateLocal.container_type==request.get('container_type'),
        FclFreightRateLocal.commodity == request.get('commodity'),
        FclFreightRateLocal.shipping_line_id==request.get('shipping_line_id'),
        FclFreightRateLocal.service_provider_id==request.get('service_provider_id')).first()

    if not fcl_freight_local:
        fcl_freight_local = FclFreightRateLocal(**row)
        fcl_freight_local.set_port()
        fcl_freight_local.data={}
        
    fcl_freight_local.sourced_by_id = request.get("sourced_by_id")
    fcl_freight_local.procured_by_id = request.get("procured_by_id")
    fcl_freight_local.selected_suggested_rate_id = request.get('selected_suggested_rate_id')

    new_free_days = {}

    if 'detention' in request['data']:
        new_free_days['detention'] = {'slabs': [] } | (request['data']['detention'] or {})

    if 'demurrage' in request['data']:
        new_free_days['demurrage'] = {'slabs': [] } | (request['data']['demurrage'] or {})

    if 'plugin' in request['data']:
        new_free_days['plugin'] = {'slabs': [] } | (request['data']['plugin'] or {})

    if request['data'].get('line_items'):
        line_items = get_normalized_line_items(request['data']['line_items'])
        fcl_freight_local.data = fcl_freight_local.data | { 'line_items': line_items }
    if 'rate_sheet_validation' not in request:
        fcl_freight_local.validate_before_save()
        fcl_freight_local.update_special_attributes(new_free_days)
    else:
        fcl_freight_local.update_special_attributes(new_free_days, True)

    if not request.get("rate_not_available_entry"):
        fcl_freight_local.rate_not_available_entry = False
    fcl_freight_local.update_freight_objects()
    create_free_days(fcl_freight_local, request)

    try:
      fcl_freight_local.save()
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))


    create_audit(request, fcl_freight_local.id)
    
    get_multiple_service_objects(fcl_freight_local)

    fcl_freight_local_data_updation.apply_async(kwargs={"request":request},queue='low')

    return {"id": fcl_freight_local.id }

def create_free_days(fcl_freight_local,request):
    if request['data'].get('detention'):
        detention_obj = {}
        detention_obj['location_id'] = request['port_id']
        detention_obj['free_days_type'] = 'detention'
        detention_obj['specificity_type'] = 'shipping_line'
        detention_obj['previous_days_applicable'] = False

        detention_obj = detention_obj | ({key: value for key, value in request['data']['detention'].items() if key in ('free_limit', 'slabs', 'remarks')})
        detention_obj = detention_obj | ({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id')})

        detention = create_fcl_freight_rate_free_day(detention_obj)
        fcl_freight_local.detention_id = detention['id']

    if request['data'].get('demurrage'):
        demurrage_obj = {}
        demurrage_obj['location_id'] = request['port_id']
        demurrage_obj['free_days_type'] = 'demurrage'
        demurrage_obj['specificity_type'] = 'shipping_line'
        demurrage_obj['previous_days_applicable'] = False

        demurrage_obj = demurrage_obj | ({key: value for key, value in request['data']['demurrage'].items() if key in ('free_limit', 'slabs', 'remarks')})
        demurrage_obj = demurrage_obj | ({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id')})

        demurrage = create_fcl_freight_rate_free_day(demurrage_obj)

        fcl_freight_local.demurrage_id = demurrage['id']

    if request['data'].get('plugin'):
        plugin_obj = {}
        plugin_obj['location_id'] = request['port_id']
        plugin_obj['free_days_type'] = 'plugin'
        plugin_obj['specificity_type'] = 'shipping_line'
        plugin_obj['previous_days_applicable'] = False

        plugin_obj = plugin_obj | ({key: value for key, value in request['data']['plugin'].items() if key in ('free_limit', 'slabs', 'remarks')})
        plugin_obj = plugin_obj | ({key: value for key, value in request.items() if key in ('performed_by_id', 'sourced_by_id', 'procured_by_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id')})

        plugin = create_fcl_freight_rate_free_day(plugin_obj)
        fcl_freight_local.plugin_id = plugin['id']

    return True



