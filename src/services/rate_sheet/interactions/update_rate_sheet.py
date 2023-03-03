
from services.rate_sheet.models.rate_sheet import RateSheet
from params import UpdateRateSheet
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudits
from services.rate_sheet.interactions.fcl_rate_sheet_converted_file import fcl_rate_sheet_converted_file
from playhouse.postgres_ext import *
from peewee import *
from rails_client import client
from fastapi.encoders import jsonable_encoder
import uuid

PROD_DATA_OPERATIONS_ASSOCIATE_ROLE_ID = ['dcdcb3d8-4dca-42c2-ba87-1a54bc4ad7fb']

def get_audit_params(parameters, location_mapping):
    audit_data = parameters
    # audit_data = @_interaction_inputs.slice(:service_name, :comment, :file_url)

    return {
        "object_type": "Location",
        "object_id": str(location_mapping.id),
        "action_name": "create",
        "performed_by_id": parameters.performed_by_id,
        "performed_by_type": parameters.performed_by_type,
        "data": audit_data,
    }


def get_relevant_user_ids(params):
    user_ids = []
    audit_data = params['audits'].filter(action_name='update').first()
    user_ids.append(audit_data.performed_by_id)
    user_ids.append(audit_data.procured_by_id)
    return user_ids


def send_rate_sheet_notifications(params):
    user_ids = []
    if params['serial_id']:
        serial_id = params['serial_id']
    else:
        serial_id = RateSheet.select(fn.MAX(RateSheet.serial_id)).scalar()

    variables = {'file_name': params['file_url'].split('/').pop(), 'serial_id': serial_id}

    if params['status'] == 'uploaded':
        user_ids = [user.user_id for user in client.ruby.list_partner_users.run(filters={
            'role_ids': PROD_DATA_OPERATIONS_ASSOCIATE_ROLE_ID,
            'status': 'active',
            'partner_status': 'active',
        }).list()]
        template_name = 'rate_sheet_uploaded'
    elif params['status'] == 'converted' or params['status'] == 'processing' or params['status'] == 'complete':
        user_ids = get_relevant_user_ids()
        if params['status'] == 'converted':
            template_name = 'rate_sheet_converted'
        elif params['status'] == 'processing':
            template_name = 'rate_sheet_processing'
        else:
            template_name = 'rate_sheet_complete'

    for user_id in user_ids:
        data = {
            'type': 'platform_notification',
            'user_id': user_id,
            'service': 'rate_sheet',
            'service_id': params['id'],
            'template_name': template_name,
            'variables': variables
        }
        client.ruby.create_communication(data)

def create_audit(request):

    audit_data = {}
    audit_data['price'] = request['price']
    audit_data['currency'] = request['currency']
    audit_data['remarks'] = request.get('remarks')

    RateSheetAudits.create(
        action_name = 'create',
        rate_sheet_id = request.get('rate_sheet_id'),
        performed_by_id = request['performed_by_id'],
        procured_by_id = request['procured_by_id'],
        sourced_by_id = request['sourced_by_id'],
        data = audit_data
    )


def update_rate_sheet(params: UpdateRateSheet):
    rate_sheet = RateSheet.get(RateSheet.id == params['id'])
    if rate_sheet.status != 'uploaded':
        return
    if 'converted_files' in params:
        for converted_file, index in params['converted_files']:
            converted_file['status'] = 'under_validation'
            converted_file['id'] = uuid.uuid()
            converted_file['service_provider_id'] = jsonable_encoder(rate_sheet.service_provider_id)
            converted_file['cogo_entity_id'] = jsonable_encoder(rate_sheet.cogo_entity_id)
            converted_file['rate_sheet_id'] = jsonable_encoder(rate_sheet.id)
            converted_file['file_index'] = index+1
    params['status'] = 'converted'
    if not rate_sheet.save():
        return
    # create_audit(get_audit_params(params, rate_sheet))
    # send_rate_sheet_notifications(params)
    print(params)
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']
    print(rate_sheet)
    rate_sheet['id'] = params['id']
    fcl_rate_sheet_converted_file(rate_sheet)

