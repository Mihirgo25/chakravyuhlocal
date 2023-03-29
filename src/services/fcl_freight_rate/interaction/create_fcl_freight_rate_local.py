from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from fastapi import HTTPException
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_free_day import create_fcl_freight_rate_free_day
from database.db_session import db
from celery_worker import fcl_freight_local_data_updation


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
        object_type = 'FclFreightRateLocal'
    )

def create_fcl_freight_rate_local(request):
    object_type = 'Fcl_Freight_Rate_Local' 
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_","")) 
    db.execute_sql(query)
    with db.atomic() as transaction:
        return execute_transaction_code(request)

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
        'service_provider_id' : request.get('service_provider_id'),
        "sourced_by_id": request.get("sourced_by_id"),
        "procured_by_id": request.get("procured_by_id"),
    }

    fcl_freight_local = FclFreightRateLocal.select().where(
        FclFreightRateLocal.port_id == request.get('port_id'),
        FclFreightRateLocal.trade_type ==request.get('trade_type'),
        FclFreightRateLocal.main_port_id == request.get('main_port_id'),
        FclFreightRateLocal.container_size==request.get('container_size'),
        FclFreightRateLocal.container_type==request.get('container_type'),
        FclFreightRateLocal.commodity == request.get('commodity'),
        FclFreightRateLocal.shipping_line_id==request.get('shipping_line_id'),
        FclFreightRateLocal.service_provider_id==request.get('service_provider_id')).first()

    if not fcl_freight_local:
        fcl_freight_local = FclFreightRateLocal(**row)
        fcl_freight_local.rate_not_available_entry = False
        fcl_freight_local.set_port()
    fcl_freight_local.selected_suggested_rate_id = request.get('selected_suggested_rate_id')
    fcl_freight_local.data = request.get('data')

    if request['data'].get('line_items'):
        fcl_freight_local.data = fcl_freight_local.data | {'line_items': request['data']['line_items']}
    
    fcl_freight_local.validate_before_save()
    
    fcl_freight_local.update_special_attributes()
    fcl_freight_local.update_freight_objects()

    try:
      fcl_freight_local.save()
    except Exception as e:
      raise HTTPException(status_code=403, detail=str(e))
    
    create_free_days(fcl_freight_local, request)
    
    create_audit(request, fcl_freight_local.id)
    
    fcl_freight_local_data_updation.apply_async(kwargs={"local_object":fcl_freight_local,"request":request},queue='low')

    return {"id": fcl_freight_local.id}

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



  