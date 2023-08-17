
from services.rate_sheet.models.rate_sheet import RateSheet
from params import UpdateRateSheet
from services.rate_sheet.models.rate_sheet_audits import RateSheetAudit
from playhouse.postgres_ext import *
from peewee import *
from fastapi.encoders import jsonable_encoder
import uuid
from services.rate_sheet.interactions.send_rate_sheet_notification import send_rate_sheet_notifications
from services.rate_sheet.interactions.create_rate_sheet_audits import create_audit
from fastapi import HTTPException
def get_audit_params(parameters):
    keys_to_extract = ['converted_files']
    audit_data = dict(filter(lambda item: item[0] in keys_to_extract, parameters.items()))
    return {
        'action_name': 'update',
        'performed_by_id': parameters.get('performed_by_id'),
        'object_id' : parameters.get('id'),
        'procured_by_id': parameters.get('procured_by_id'),
        'sourced_by_id': parameters.get('sourced_by_id'),
        "performed_by_type": parameters.get('performed_by_type'),
        'data': audit_data
    }



def update_rate_sheet(params: UpdateRateSheet):
    from celery_worker import validate_and_process_rate_sheet_converted_file_delay
    rate_sheet = RateSheet.get(RateSheet.id == params['id'])
    if rate_sheet.status not in ['uploaded', 'partially_complete']:
        raise HTTPException(status_code=400, detail= "File already uploaded")
    if 'converted_files' in params:
        index = 0
        for converted_file in params.get('converted_files'):
                converted_file['status'] = 'under_validation'
                converted_file['id'] = '{}_{}'.format(rate_sheet.id, str(uuid.uuid4()))
                converted_file['service_provider_id'] = str(rate_sheet.service_provider_id)
                converted_file['cogo_entity_id'] = str(rate_sheet.cogo_entity_id)
                converted_file['rate_sheet_id'] = str(rate_sheet.id)
                converted_file['file_index'] = index+1
                converted_file['rates_count'] = 0
                converted_file['valid_rates_count'] = 0
    params['status'] = 'processing'
    rate_sheet.converted_files = params.get('converted_files')
    rate_sheet.status = params['status']
    rate_sheet.save()
    create_audit(get_audit_params(params))
    send_rate_sheet_notifications(params)
    rate_sheet = jsonable_encoder(rate_sheet)['__data__']

    for key in params.keys():
        if key not in ['id', 'performed_by_id', 'procured_by_id','sourced_by_id']:
            rate_sheet[key] = params[key]
    validate_and_process_rate_sheet_converted_file_delay.apply_async(kwargs={'request':rate_sheet},queue='critical')
    return {
      "id": rate_sheet['id']
    }

