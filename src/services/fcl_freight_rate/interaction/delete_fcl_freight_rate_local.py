from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from services.fcl_freight_rate.models.fcl_services_audit import FclServiceAudit
from fastapi import HTTPException
from database.db_session import db

def delete_fcl_freight_rate_local(request):
    with db.atomic() as transaction:
        try:
            return execute_transaction_code(request)
        except Exception as e:
            transaction.rollback()
            return e

def execute_transaction_code(request):
    object = find_object(request)

    if not object:
        raise HTTPException(status_code=499, detail="Freight rate local id not found")

    # object.update_columns(get_delete_params())
    for key, value in delete_params.items():
        setattr(object, key, value)
    object.save()

    create_audit(request, object.id)

    return {
      id: object.id
    }

def create_audit(request, freight_rate_local_id):
    FclServiceAudit.create(
        action_name = 'delete',
        performed_by_id = request['performed_by_id'],
        bulk_operation_id = request.get('bulk_operation_id'),
        data = delete_params,
        object_id = freight_rate_local_id,
        object_type = 'FclFreightRateLocal'
    )

def find_object(request):
    try:
        object = FclFreightRateLocal.get_by_id(request['id'])
    except:
        object = None
    return object

# def get_delete_params():
delete_params = {
        'line_items': [],
        'data': {},
        'is_line_items_error_messages_present': None,
        'is_line_items_info_messages_present': None,
        'line_items_error_messages': None,
        'line_items_info_messages': None,
        'rate_not_available_entry': True,
        'detention_id': None,
        'demurrage_id': None,
        'is_detention_slabs_missing': None,
        'is_demurrage_slabs_missing': None,
        'is_plugin_slabs_missing': None
}
