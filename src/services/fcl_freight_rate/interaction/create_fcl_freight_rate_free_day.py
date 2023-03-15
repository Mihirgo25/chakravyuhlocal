from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
from services.fcl_freight_rate.helpers.find_or_initialize import find_or_initialize
from database.db_session import db
from fastapi import HTTPException
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def create_fcl_freight_rate_free_day(request):
    with db.atomic() as transaction:
          try:
              return execute_transaction_code(request)
          except Exception as e:
              transaction.rollback()
              return e

def execute_transaction_code(request):

    free_day = get_free_day_object(request)

    # free_day.validate_validity_object(request['validity_start'], request['validity_end'])

    free_day.validate_before_save()
    free_day.update_special_attributes()

    try:
        free_day.save()
    except:
        raise HTTPException(status_code=403, detail='fcl freight rate free day did not save')
    
    # if 'shipment_id' in request:
    #     free_day.update_sell_quotation()

    create_audit(request, free_day.id)

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
        'importer_exporter_id' : request.get('importer_exporter_id')
        # 'validity_start' : request.get('validity_start')
        # 'validity_end' : request.get('validity_end')
    }

    free_day = find_or_initialize(FclFreightRateFreeDay, **row)

    extra_fields = ['previous_days_applicable','free_limit','remarks','slabs']
    for field in extra_fields:
        if field in request:
            setattr(free_day, field, request[field])

    free_day.rate_not_available_entry = False

    return free_day

def create_audit(request, free_day_id):
    audit_data = {'free_limit' : request.get('free_limit'), 'remarks' : request.get('remarks'), 'slabs' : request.get('slabs')}

    try:
        FclFreightRateAudit.create(
            action_name = 'create',
            performed_by_id = request['performed_by_id'],
            rate_sheet_id = request.get('rate_sheet_id'),
            procured_by_id = request['procured_by_id'],
            sourced_by_id = request['sourced_by_id'],
            data = audit_data,
            object_id = free_day_id,
            object_type = 'FclFreightRateFreeDay'
        )
    except:
        raise HTTPException(status_code=403, detail='fcl freight audit did not save')
