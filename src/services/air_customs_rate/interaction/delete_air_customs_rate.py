from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from database.db_session import db
from fastapi import HTTPException

def delete_air_customs_rate(request):
    with db.atomic():
        return execute_transaction_code(request)

def execute_transaction_code(request):
    rate_object = find_rate_object(request)
    if not rate_object:
        raise HTTPException(status_code=404, detail='Rate Not Found')

    delete_params = get_params_for_deletion()

    for key in list(delete_params.keys()):
        setattr(rate_object, key, delete_params[key])

    try:
        rate_object.save()
    except Exception as e:
        raise HTTPException(status_code=500, detail = 'Error while deleting rate')

    create_audit_for_delete_rates(request, rate_object.id, delete_params)

    return {
      'id': rate_object.id
    }

def find_rate_object(request):
    try:
        rate_object = AirCustomsRate.select().where(AirCustomsRate.id == request['id']).first()
    except:
        rate_object = None
    return rate_object

def create_audit_for_delete_rates(request, rate_object_id, delete_params):
    AirCustomsRateAudit.create(
        action_name = 'delete',
        performed_by_id = request.get('performed_by_id'),
        bulk_operation_id = request.get('bulk_operation_id'),
        object_id = rate_object_id,
        object_type = 'AirCustomsRate',
        data = delete_params
    )

def get_params_for_deletion():
    return {
      'line_items': [],
      'rate_not_available_entry': True,
      'is_line_items_error_messages_present': None,
      'is_line_items_info_messages_present': None,
      'line_items_error_messages': None,
      'line_items_info_messages': None
    }