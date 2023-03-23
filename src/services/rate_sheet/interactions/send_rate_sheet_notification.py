
from services.rate_sheet.models.rate_sheet import RateSheet
from playhouse.postgres_ext import *
from peewee import *
from micro_services.client import *
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit



PROD_DATA_OPERATIONS_ASSOCIATE_ROLE_ID = ['dcdcb3d8-4dca-42c2-ba87-1a54bc4ad7fb']

def get_relevant_user_ids(params):
    user_ids = []
    audit_data = RateSheetAudit.select().where(RateSheetAudit.action_name == 'update').limit(1)
    audit_data = audit_data.dicts().get()
    user_ids.append(str(audit_data['performed_by_id']))
    user_ids.append(str(audit_data['procured_by_id']))
    return user_ids

def send_rate_sheet_notifications(params):
    user_ids = []
    if params.get('serial_id'):
        serial_id = params.get('serial_id')
    else:
        serial_id = RateSheet.select(fn.MAX(RateSheet.serial_id)).scalar()
    print(params)
    try:
        variables = {'file_name': params.get('converted_files')[0].get('file_url').split('/').pop(), 'serial_id': serial_id}
    except:
        variables = {'file_name': params.get('file_url').split('/').pop(), 'serial_id': serial_id}

    if params.get('status') == 'uploaded':
        user_ids = [user.user_id for user in common.list_partner_users.run(filters={
            'role_ids': PROD_DATA_OPERATIONS_ASSOCIATE_ROLE_ID,
            'status': 'active',
            'partner_status': 'active',
        }).list()]
        template_name = 'rate_sheet_uploaded'
    elif params.get('status') == 'converted' or params.get('status') == 'processing' or params.get('status') == 'complete':
        user_ids = get_relevant_user_ids(params)
        if params.get('status') == 'converted':
            template_name = 'rate_sheet_converted'
        elif params.get('status') == 'processing':
            template_name = 'rate_sheet_processing'
        else:
            template_name = 'rate_sheet_complete'

    for user_id in user_ids:
        data = {
            'type': 'platform_notification',
            'user_id': user_id,
            'service': 'rate_sheet',
            'service_id': params.get('id'),
            'template_name': template_name,
            'variables': variables
        }
        common.create_communication(data)
