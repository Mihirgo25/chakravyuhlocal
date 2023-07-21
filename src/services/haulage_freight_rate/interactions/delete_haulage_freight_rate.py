from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from database.db_session import db
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from fastapi import HTTPException
from services.haulage_freight_rate.interactions.update_haulage_freight_rate_platform_prices import update_haulage_freight_rate_platform_prices

def delete_haulage_freight_rate(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    """
    Delete Haulage Freight Rates
    Response Format:
        {"id": deleted_haulage_freight_rate_id}
    """
    
    object = find_object(request)

    delete_params = get_delete_params()
    for key,value in delete_params.items():
        setattr(object, key, value)

    try:
        object.save()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Exception in saving haulage freight rate")

    create_audit(request, object.id, delete_params)

    object.update_platform_prices_for_other_service_providers()

    return {
      'id': object.id
    }

def create_audit(request, freight_id,audit_data):
    HaulageFreightRateAudit.create(
        action_name = 'delete',
        performed_by_id = request['performed_by_id'],
        bulk_operation_id = request.get('bulk_operation_id'),
        data = audit_data,
        object_id = freight_id,
        object_type = 'HaulageFreightRate',
        sourced_by_id = request['sourced_by_id'],
        procured_by_id = request['procured_by_id']
    )

def find_object(request):
    object = HaulageFreightRate.select().where(HaulageFreightRate.id == request.get('id'))
    if object.count()>0:
        return object.first()
    else:
        raise HTTPException(status_code=404, detail="Rate id not found")

def get_delete_params():
    return  {
        "line_items": [],
        "transit_time": None,
        "detention_free_time": None,
        "trailer_type": None,
        "trip_type": None,
        "rate_not_available_entry": True,
        "platform_price": None,
        "is_best_price": None,
        "is_line_items_error_messages_present": None,
        "is_line_items_info_messages_present": None,
        "line_items_error_messages": None,
        "line_items_info_messages": None
    }

