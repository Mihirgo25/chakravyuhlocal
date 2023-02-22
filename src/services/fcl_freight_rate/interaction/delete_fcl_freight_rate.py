from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal

def delete_fcl_freight_rate_local(request):
    object = find_object(request)

    if not object:
        # self.errors.add('{} is invalid'.format(request['id']))
        return 

    updated_object = object.update(get_delete_params())

    # object.audits.create!(get_audit_params(request))

    return {
      id: updated_object.id
    }

def get_audit_params(request):
    params = { 
        'action_name': 'delete',
        'performed_by_id': request['performed_by_id'],
        'bulk_operation_id':   request['bulk_operation_id'],
        'procured_by_id':  request['procured_by_id'],
        'sourced_by_id':   request['sourced_by_id'],
        'data': get_delete_params()
    }
    return params

def find_object(request):
    try:
        object = FclFreightRateLocal.select.where(FclFreightRateLocal.id == request['id'])
    except:
        object = None
    return object

def get_delete_params():
    return {
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