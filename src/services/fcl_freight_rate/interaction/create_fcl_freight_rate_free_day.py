from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from database.db_session import db
from fastapi import HTTPException
from datetime import datetime, timedelta
from celery_worker import update_multiple_service_objects


def create_fcl_freight_rate_free_day(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request):
    request["validity_start"] = (request.get('validity_start') or datetime.now().date())
    request["validity_end"] = (request.get('validity_end') or (datetime.now() + timedelta(days=90)).date())
    free_day = get_free_day_object(request)

    free_day.validate_validity_object(request['validity_start'], request['validity_end'])

    free_day.validate_before_save()

    free_day.update_special_attributes()

    try:
        free_day.save()
    except:
        raise HTTPException(status_code=500, detail='fcl freight rate free day did not save')

    # if 'shipment_id' in request:
    #     free_day.update_sell_quotation()
    create_audit(request, free_day.id)

    update_multiple_service_objects.apply_async(kwargs={'object':free_day},queue='low')

    return {"id": free_day.id}

def get_free_day_object(request):
    row = {
        'location_id' : request['location_id'],
        'trade_type' : request['trade_type'],
        'free_days_type' : request['free_days_type'],
        'container_type' : request['container_type'],
        'container_size' : request['container_size'],
        'shipping_line_id' : request['shipping_line_id'],
        'service_provider_id' : request['service_provider_id'],
        'specificity_type' : request['specificity_type'],
        'importer_exporter_id' : request.get('importer_exporter_id'),
        'sourced_by_id' : request.get('sourced_by_id'),
        'procured_by_id' : request.get('procured_by_id'),
        'validity_start' : request.get('validity_start'),
        'validity_end' : request.get('validity_end')
    }
    free_day = FclFreightRateFreeDay.select().where(
        FclFreightRateFreeDay.location_id == request['location_id'],
        FclFreightRateFreeDay.trade_type == request['trade_type'],
        FclFreightRateFreeDay.free_days_type == request['free_days_type'],
        FclFreightRateFreeDay.container_type == request['container_type'],
        FclFreightRateFreeDay.container_size == request['container_size'],
        FclFreightRateFreeDay.shipping_line_id == request['shipping_line_id'],
        FclFreightRateFreeDay.service_provider_id == request['service_provider_id'],
        FclFreightRateFreeDay.specificity_type == request['specificity_type']
    )

    if row['importer_exporter_id']:
        free_day = free_day.where(FclFreightRateFreeDay.importer_exporter_id == row['importer_exporter_id'])
    else:
        free_day = free_day.where(FclFreightRateFreeDay.importer_exporter_id == None)
    free_day = free_day.first()
    if not free_day:
        free_day = FclFreightRateFreeDay(**row)

    extra_fields = ['previous_days_applicable','free_limit','remarks','slabs']
    for field in extra_fields:
        if field in request:
            setattr(free_day, field, request[field])

    free_day.rate_not_available_entry = False

    return free_day

def create_audit(request, free_day_id):
    object_type = 'Fcl_Freight_Rate_Free_Day'
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
    db.execute_sql(query)
    audit_data = {'free_limit' : request.get('free_limit'), 'remarks' : request.get('remarks'), 'slabs' : request.get('slabs')}

    try:
        FclServiceAudit.create(
            action_name = 'create',
            performed_by_id = request['performed_by_id'],
            rate_sheet_id = request.get('rate_sheet_id'),
            data = audit_data,
            object_id = free_day_id,
            object_type = 'FclFreightRateFreeDay'
        )
    except:
        raise HTTPException(status_code=500, detail='Fcl Freight Audit did not save')
