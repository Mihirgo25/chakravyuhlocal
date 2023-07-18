from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from database.db_session import db
from fastapi import HTTPException

def create_audit(request, freight_id, audit_data):
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
        action_name = 'delete',
        performed_by_id = request.get('performed_by_id'),
        bulk_operation_id = request.get('bulk_operation_id'),
        data = audit_data,
        object_id = freight_id,
        object_type = 'FtlFreightRate',
        sourced_by_id = request.get('sourced_by_id'),
        procured_by_id = request.get('procured_by_id')
    )

def delete_ftl_freight_rate(request):
    with db.atomic():
        return execute_transaction_code(request)
    
def execute_transaction_code(request):
    object = find_object(request)

    delete_params = get_delete_params()
    for key,value in delete_params.items():
        setattr(object, key, value)

    try:
        object.save()
    except Exception as e:
        print("Exception in saving haulage freight rate", e)

    create_audit(request, object.id, delete_params)

    object.update_platform_prices_for_other_service_providers()

    return {
      'id': object.id
    }


def find_object(request):
    object = FtlFreightRate.select().where(FtlFreightRate.id == request.get('id'))
    if object.count()>=0:
        return object.first()
    else:
        raise HTTPException(status_code=400, detail="Rate id not found")
    
def get_delete_params():
    data = {
        'line_items': [],
        'rate_not_available_entry': True,
        'platform_price': None,
        'is_best_price': None,
        'is_line_items_error_messages_present': None,
        'is_line_items_info_messages_present': None,
        'line_items_error_messages': None,
        'line_items_info_messages': None
    }
    return data