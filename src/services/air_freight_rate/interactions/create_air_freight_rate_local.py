from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from fastapi import HTTPException
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from database.db_session import db
from libs.get_multiple_service_objects import get_multiple_service_objects

def create_air_freight_rate_local(request):
    object_type='Air_Freight_Rate_Local'
    query="create table if not exists air_services_audits_{} partition of air_services_audits for values in ('{}')".format(object_type.lower(),object_type.replace("_",""))
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    from services.air_freight_rate.air_celery_worker import update_air_freight_rate_local_job_on_rate_addition_delay
    row={
        'airport_id':request.get('airport_id'),
        'airline_id':request.get('airline_id'),
        'trade_type':request.get('trade_type'),
        'commodity':request.get('commodity'),
        'service_provider_id':request.get('service_provider_id'),
        'commodity_type': request.get('commodity_type'),
        'rate_type': request.get('rate_type'),
        'importer_exporter_id':request.get('importer_exporter_id')
    }

    air_freight_local=AirFreightRateLocal.select().where(
        AirFreightRateLocal.airport_id == request.get('airport_id'),
        AirFreightRateLocal.airline_id ==request.get('airline_id'),
        AirFreightRateLocal.trade_type == request.get('trade_type'),
        AirFreightRateLocal.commodity== request.get('commodity'),
        AirFreightRateLocal.commodity_type == request.get('commodity_type'),
        AirFreightRateLocal.rate_type == request.get('rate_type'),
        AirFreightRateLocal.service_provider_id==request.get('service_provider_id'),
        AirFreightRateLocal.importer_exporter_id == request.get('importer_exporter_id')).first()

    if not air_freight_local:
        air_freight_local=AirFreightRateLocal(**row)
        air_freight_local.set_locations()
        air_freight_local.set_airline()
        air_freight_local.set_location_ids()

    old_line_items = air_freight_local.line_items
    if not old_line_items:
        old_line_items=[]
    for line_item in request.get('line_items'):
        add_line_item(old_line_items, line_item)

    air_freight_local.line_items = old_line_items
    air_freight_local.sourced_by_id = request.get('sourced_by_id')
    air_freight_local.procured_by_id = request.get('procured_by_id')
    air_freight_local.rate_not_available_entry = False
    if 'rate_sheet_validation' not in request:
        air_freight_local.validate()


    try:
        air_freight_local.save()
    except Exception:
        raise HTTPException(status_code=400, detail="rate did not save")

    create_audit(request,air_freight_local.id)

    air_freight_local.update_freight_objects()

    air_freight_local.update_line_item_messages()

    air_freight_local.update_foreign_references()

    get_multiple_service_objects(air_freight_local)

    update_air_freight_rate_local_job_on_rate_addition_delay.apply_async(kwargs={'request': request, "id": air_freight_local.id},queue='fcl_freight_rate')

    return {
      'id': str(air_freight_local.id)
    }


def add_line_item(old_line_items,line_item):
    is_new_line_item = True
    for index,old_line_item in enumerate(old_line_items or []):
        if old_line_item['code'] == line_item['code']:
            is_new_line_item = False
            old_line_items[index] = line_item
    if is_new_line_item:
        old_line_items.append(line_item)
    return old_line_items

def create_audit(request,air_freight_local_id):
    audit_data={}
    audit_data['data'] = request.get('data')
    audit_data['selected_suggested_rate_id'] = request.get('selected_suggested_rate_id')

    id =AirServiceAudit.create(
        action_name = 'create',
        rate_sheet_id = request.get('rate_sheet_id'),
        bulk_operation_id=request.get('bulk_operation_id'),
        data = audit_data,
        object_id = air_freight_local_id,
        object_type = 'AirFreightRateLocal')

    return id