from fastapi import HTTPException
from database.db_session import db
from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from configs.global_constants import DEFAULT_SERVICE_PROVIDER_ID

def create_audit(haulage_id, request, transport_modes):
    audit_data = {
        'line_items': request.get('line_items')
    }
    if 'trailer' in transport_modes:
        object_type = 'TrailerFreightRate'
    else:
        object_type = 'HaulageFreightRate'

    HaulageFreightRateAudit.create(
        action_name = 'update',
        object_id = haulage_id,
        object_type = object_type,
        performed_by_id = request.get("performed_by_id"),
        bulk_operation_id = request.get("bulk_operation_id"),
        data = audit_data,
        sourced_by_id = request.get('sourced_by_id'),
        procured_by_id = request.get('procured_by_id')
    )

def update_haulage_freight_rate(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    from services.haulage_freight_rate.haulage_celery_worker import update_haulage_freight_rate_job_on_rate_addition_delay
    haulage = find_haulage_object(request)

    update_params =  {
        'procured_by_id':request.get('procured_by_id'),
        'sourced_by_id':request.get('sourced_by_id'),
        'line_items':request.get('line_items')
    }

    for key in list(update_params.keys()):
        setattr(haulage, key, update_params[key])

    haulage.update_line_item_messages(haulage.possible_charge_codes())
    haulage.set_platform_price()
    haulage.set_is_best_price()
    haulage.update_platform_prices_for_other_service_providers()

    create_audit(haulage.id, request, haulage.transport_modes)

    try:
        haulage.save()
    except Exception as e:
        print("Exception in updating rate", e)
    
    if str(haulage.service_provider_id) != DEFAULT_SERVICE_PROVIDER_ID:
        update_haulage_freight_rate_job_on_rate_addition_delay.apply_async(kwargs={'request': request, "id": haulage.id},queue='fcl_freight_rate')

    return {"id": haulage.id}

def find_haulage_object(request):
    query = HaulageFreightRate.select().where(HaulageFreightRate.id==request.get("id"))
    if query.count()>0:
        return query.first()
    else:
        raise HTTPException(status_code=404, detail="Rate Not Found")
   