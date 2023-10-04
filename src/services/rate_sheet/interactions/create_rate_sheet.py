
from services.rate_sheet.models.rate_sheet import RateSheet
from params import CreateRateSheet
from playhouse.postgres_ext import *
from peewee import *
from services.rate_sheet.interactions.send_rate_sheet_notification import send_rate_sheet_notifications
from services.rate_sheet.interactions.create_rate_sheet_audits import create_audit
from database.rails_db import get_eligible_orgs
from fastapi import HTTPException



def get_audit_params(parameters):
    keys_to_extract = ["service_name","comment","file_url"]
    audit_data = dict(filter(lambda item: item[0] in keys_to_extract, parameters.items()))
    return {
        "action_name": "create",
        "performed_by_id": parameters.get('performed_by_id'),
        "procured_by_id": parameters.get('procured_by_id'),
        "sourced_by_id": parameters.get('sourced_by_id'),
        "object_id": parameters.get('object_id'),
        "performed_by_type": parameters.get('performed_by_type'),
        "data": audit_data,
    }

def get_create_params(params):
    keys_to_extract = ["performed_by_id","procured_by_id","sourced_by_id"]
    relevant_params = dict(filter(lambda item: item[0] not in keys_to_extract, params.items()))
    relevant_params['status'] = 'uploaded'
    relevant_params['agent_id'] = params.get('procured_by_id')
    return relevant_params

def validate_service_provider_id(service_provider_id, service_name):
    service_provider_data = get_eligible_orgs(service=service_name)
    if str(service_provider_id) in service_provider_data:
        return True
    raise HTTPException(status_code = 400, detail = 'Service Provider Id Is Not Valid')


def create_rate_sheet(params: CreateRateSheet):
    validate_service_provider_id(params.get('service_provider_id'), params.get('service_name'))
    rate_sheet = RateSheet.create(**get_create_params(params))
    params['object_id'] = str(rate_sheet.id)
    create_audit(get_audit_params(params))
    send_rate_sheet_notifications(params)
    return  {"id": params.get('object_id')}
