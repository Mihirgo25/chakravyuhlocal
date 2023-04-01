from services.fcl_freight_rate.models.fcl_freight_rate_weight_limit import FclFreightRateWeightLimit
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from database.db_session import db
from fastapi import HTTPException

def create_fcl_freight_rate_weight_limit(request):
    object_type = 'Fcl_Freight_Rate_Weight_Limit'
    query = "create table if not exists fcl_services_audits_{} partition of fcl_services_audits for values in ('{}')".format(object_type.lower(), object_type.replace("_",""))
    db.execute_sql(query)
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    from celery_worker import update_multiple_service_objects
    weight_limit = get_weight_limit_object(request)

    weight_limit.validate_before_save()
    weight_limit.update_special_attributes()

    try:
        weight_limit.save()
    except:
        raise HTTPException(status_code=500, detail='fcl freight rate weight limit did not save')
    update_multiple_service_objects.apply_async(kwargs={"object":weight_limit},queue='low')
    create_audit(request, weight_limit.id)
    return {"id": weight_limit.id}

def get_weight_limit_object(request):
    row = {
      'origin_location_id': request['origin_location_id'],
      'destination_location_id': request['destination_location_id'],
      'container_size': request['container_size'],
      'container_type': request['container_type'],
      'shipping_line_id': request['shipping_line_id'],
      'service_provider_id': request['service_provider_id'],
      'sourced_by_id':request['sourced_by_id'],
      'procured_by_id':request['procured_by_id']
    }

    weight_limit = FclFreightRateWeightLimit.select().where(
        FclFreightRateWeightLimit.origin_location_id == request['origin_location_id'],
        FclFreightRateWeightLimit.destination_location_id == request['destination_location_id'],
        FclFreightRateWeightLimit.container_size == request['container_size'],
        FclFreightRateWeightLimit.container_type == request['container_type'],
        FclFreightRateWeightLimit.shipping_line_id == request['shipping_line_id'],
        FclFreightRateWeightLimit.service_provider_id == request['service_provider_id']).first()

    if not weight_limit:
        weight_limit = FclFreightRateWeightLimit(**row)

    extra_fields = ['free_limit','remarks','slabs']
    for field in extra_fields:
       if field in request:
          setattr(weight_limit, field, request[field])

    return weight_limit

def create_audit(request, weight_limit_id):
    audit_data = {'free_limit' : request.get('free_limit'), 'remarks' : request.get('remarks'), 'slabs' : request.get('slabs')}

    try:
        FclServiceAudit.create(
        action_name = 'create',
        performed_by_id = request['performed_by_id'],
        rate_sheet_id = request.get('rate_sheet_id'),
        data = audit_data,
        object_id = weight_limit_id,
        object_type = 'FclFreightRateWeightLimit'
      )
    except:
      raise HTTPException(status_code=500, detail='fcl freight audit did not save')
