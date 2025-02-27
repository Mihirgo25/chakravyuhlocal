from database.db_session import db
from fastapi import HTTPException
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from configs.global_constants import DEFAULT_SERVICE_PROVIDER_ID

def create_audit(ftl_id, request):
    audit_data = {
        'line_items': request.get('line_items'),
        'transit_time': request.get('transit_time'),
        'detention_free_time': request.get('detention_free_time'),
        'validity_start': str(request.get('validity_start')),
        'validity_end': str(request.get('validity_end')),
        'minimum_chargeable_weight': request.get('minimum_chargeable_weight'),
        'truck_body_type': request.get('truck_body_type')
    }

    FtlFreightRateAudit.create(
        action_name = 'update',
        object_id = ftl_id,
        object_type = 'FtlFreightRate',
        performed_by_id = request.get("performed_by_id"),
        bulk_operation_id = request.get("bulk_operation_id"),
        sourced_by_id = request.get("sourced_by_id"),
        procured_by_id = request.get("procured_by_id"),
        data = audit_data
    )

def update_ftl_freight_rate(request):
    with db.atomic():
      return execute_transaction_code(request)

def execute_transaction_code(request):
    from services.ftl_freight_rate.ftl_celery_worker import update_ftl_freight_rate_job_on_rate_addition_delay
    rate_object = find_ftl_object(request)
    update_params = {}
    for params in request.keys():
        if request.get(params) is not None:
            update_params[params] = request[params]

    for key in list(update_params.keys()):
            setattr(rate_object, key, update_params[key])

    rate_object.update_line_item_messages(rate_object.possible_charge_codes())
    rate_object.set_platform_price()
    rate_object.set_is_best_price()
    rate_object.update_platform_prices_for_other_service_providers()
    rate_object.rate_not_available_entry = False

    create_audit(rate_object.id, request)

    try:
        rate_object.save()
    except Exception as error_message:
        raise HTTPException(status_code=500,detail=error_message)
    
    if str(rate_object.service_provider_id) != DEFAULT_SERVICE_PROVIDER_ID:
        update_ftl_freight_rate_job_on_rate_addition_delay.apply_async(kwargs={'request': request, "id": rate_object.id},queue='fcl_freight_rate')

    return {"id": rate_object.id}

def find_ftl_object(request):
    query = FtlFreightRate.select().where(FtlFreightRate.id==request.get("id")).first()
    if query:
        return query
    else:
        raise HTTPException(status_code=400, detail="Rate Not Found")
