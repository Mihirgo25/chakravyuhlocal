from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit
import datetime
from database.db_session import db
from fastapi import HTTPException


def find_or_initialize(**kwargs):
    try:
        obj = FclFreightRateWeightLimit.get(**kwargs)
        obj.updated_at = datetime.datetime.now()
    except FclFreightRateWeightLimit.DoesNotExist:
        obj = FclFreightRateWeightLimit(**kwargs)
    return obj

def create_fcl_freight_rate_weight_limit(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except:
            transaction.rollback()
            return "Creation Failed"

def execute_transaction_code(request):
    weight_limit = get_weight_limit_object(request)

    weight_limit.validate_before_save()

    try:
        weight_limit.save()
    except:
        raise HTTPException(status_code=499, detail='fcl freight rate weight limit did not save')

    weight_limit.update_special_attributes()
    weight_limit.save()

    # weight_limit.update_freight_objects()

    create_audit(request, weight_limit.id)

    return {"id": weight_limit.id}

def get_weight_limit_object(request):
    row = {
      'origin_location_id': request['origin_location_id'],
      'destination_location_id': request['destination_location_id'],
      'container_size': request['container_size'],
      'container_type': request['container_type'],
      'shipping_line_id': request['shipping_line_id'],
      'service_provider_id': request['service_provider_id']
    }
    weight_limit = find_or_initialize(**row)

    extra_fields = ['free_limit','remarks','slabs']
    for field in extra_fields:
       if field in request:
          setattr(weight_limit, field, request[field])
        #   var = attrgetter(field)(weight_limit) #remove var
        #   if var:
        #      if var != request[field]:
        #       setattr(weight_limit, field, request[field])
        #   else:
        #      setattr(weight_limit, field, request[field])

    return weight_limit

def create_audit(request, weight_limit_id):

    audit_data = {'free_limit' : request.get('free_limit'), 'remarks' : request.get('remarks'), 'slabs' : request.get('slabs')}

    try:
      audit = FclFreightRateAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        rate_sheet_id = request.get('rate_sheet_id'),
        procured_by_id = request['procured_by_id'],
        sourced_by_id = request['sourced_by_id'],
        data = audit_data,
        object_id = weight_limit_id,
        object_type = 'FclFreightRateWeightLimit'
      )
    except:
      raise HTTPException(status_code=499, detail='fcl freight audit did not save')
