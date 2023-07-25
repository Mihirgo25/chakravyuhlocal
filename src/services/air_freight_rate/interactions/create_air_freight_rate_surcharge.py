from services.air_freight_rate.models.air_freight_rate_surcharge import AirFreightRateSurcharge
from fastapi import HTTPException
from services.air_freight_rate.models.air_services_audit import AirServiceAudit
from database.db_session import db

def create_audit(request,surcharge_id):
    audit_data={}
    audit_data['line_items']=request.get('line_items')
    id = AirServiceAudit.create(
        action_name = 'create',
        rate_sheet_id = request.get('rate_sheet_id'),
        performed_by_id = request.get('performed_by_id'),
        bulk_operation_id=request.get('bulk_operation_id'),
        data = audit_data,
        object_id = surcharge_id,
        object_type = 'AirFreightRateSurcharge')
    return id

def create_air_freight_rate_surcharge(request):
    object_type = 'Air_Freight_Rate_Surcharge'
    query="create table if not exists air_services_audits_{} partition of air_services_audits for values in ('{}')".format(object_type.lower(),object_type.replace("_",""))
    db.execute_sql(query)    
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    from celery_worker import update_multiple_service_objects

    row = {
        'origin_airport_id' : request.get("origin_airport_id"),
        'destination_airport_id' : request.get("destination_airport_id"),
        'commodity_type' : request.get("commodity_type"),
        'commodity' : request.get("commodity"),
        'airline_id': request.get("airline_id"),
        'operation_type':request.get('operation_type'),
        'service_provider_id':request.get('service_provider_id')
        }
    surcharge = AirFreightRateSurcharge.select().where(
        AirFreightRateSurcharge.origin_airport_id == request.get("origin_airport_id"),
        AirFreightRateSurcharge.destination_airport_id == request.get("destination_airport_id"),
        AirFreightRateSurcharge.commodity_type == request.get("commodity_type"),
        AirFreightRateSurcharge.commodity == request.get("commodity"),
        AirFreightRateSurcharge.airline_id == request.get("airline_id"),
        AirFreightRateSurcharge.operation_type == request.get("operation_type"),
        AirFreightRateSurcharge.service_provider_id == request.get("service_provider_id")).first()

    
    if not surcharge:
        surcharge = AirFreightRateSurcharge(**row)
        surcharge.line_items=request.get('line_items')
        surcharge.set_locations()
        surcharge.set_destination_location_ids()
        surcharge.set_origin_location_ids()
    else:
        old_line_items= surcharge.line_items
        if not old_line_items:
            old_line_items = []
        for line_item in request.get('line_items'):
            old_line_items = add_line_item(old_line_items, line_item)
        surcharge.line_items = old_line_items
    
    surcharge.update_freight_objects()

    surcharge.update_line_item_messages()
    
    if 'rate_sheet_validation' not in request:
        surcharge.validate()

    surcharge.sourced_by_id = request.get('sourced_by_id')

    surcharge.procured_by_id = request.get('procured_by_id')
    try:
        surcharge.save()
    except Exception:
        raise HTTPException(status_code=400, detail="Rate Did Not Save")
    
    create_audit(request,surcharge.id)
    update_multiple_service_objects.apply_async(kwargs={'object':surcharge},queue='low')

    return {
      'id': str(surcharge.id)
    }
    
def add_line_item(old_line_items, line_item):
    is_new_line_item = True
    for index, old_line_item in enumerate(old_line_items):
        if old_line_item['code'] == line_item['code']:
            is_new_line_item = False
            old_line_items[index] = line_item

    if is_new_line_item:
        old_line_items.append(line_item)
    return old_line_items