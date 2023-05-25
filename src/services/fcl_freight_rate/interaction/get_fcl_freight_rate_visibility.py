from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from database.rails_db import get_organization
from micro_services.client import organization
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE

def get_fcl_freight_rate_visibility(request):
    response_object = {'reason': '', 'is_rate_available': False, 'is_visible': False }

    org_details = get_organization(id=request['service_provider_id'])[0]

    if org_details:
        org_services_data = organization.list_organization_services({'filters':{'organization_id' : str(org_details['id']), 'status' : 'active'}})
        if org_services_data:
            org_services_data = org_services_data['list']
        else:
            org_services_data = []
        org_services = [service['service'] for service in org_services_data]

    kyc_and_service_status = is_kyc_verified_and_service_validation_status(org_details, org_services)
    if kyc_and_service_status:
        response_object['reason'] += kyc_and_service_status

    fcl_freight_rate_data = get_fcl_freight_rate_data(request)

    if (not fcl_freight_rate_data) or ((not request['from_date']) or (not request['to_date'])):
        response_object['is_visible'] = False
        if (not request['from_date']) or (not request['to_date']):
            response_object['is_visible'] = False
        return response_object

    weight_limit_status = is_weight_limit_verified(fcl_freight_rate_data)
    if weight_limit_status:
        response_object['reason'] += weight_limit_status

    response_object['is_visible'] = not response_object['reason']
    response_object['is_rate_available'] = True if fcl_freight_rate_data else False
    return response_object

def is_kyc_verified_and_service_validation_status(org_details, org_services):
    kyc_and_service_reason = ''
    if not org_details:
        kyc_and_service_reason += ' service provider not present'
    if org_details and org_details['kyc_status'] != 'verified':
        kyc_and_service_reason += f" kyc status is f{org_details['kyc_status'].replace('_' , ' ')},"
    if org_details and org_details['status'] == 'inactive':
        kyc_and_service_reason += ' service provider status is inactive,'
    if (not org_services) or 'fcl_freight' not in org_services:
        kyc_and_service_reason += ' fcl service is not activated for the organization,'

    return kyc_and_service_reason


def get_fcl_freight_rate_data(request):
    fcl_freight_rate_data = None

    if request['rate_id']:
        fcl_freight_rate_data = FclFreightRate.select().where(FclFreightRate.id == request['rate_id']).first()
    else:
        fcl_freight_rate_data = FclFreightRate.select().where(
            FclFreightRate.id  == request['origin_port_id'],
            FclFreightRate.destination_port_id == request['destination_port_id'],
            FclFreightRate.container_size  ==  request['container_size'],
            FclFreightRate.container_type  ==  request['container_type'],
            FclFreightRate.commodity  ==  request['commodity'],
            FclFreightRate.service_provider_id  ==  request['service_provider_id'],
            FclFreightRate.shipping_line_id  ==  request['shipping_line_id'],
            FclFreightRate.rate_type == DEFAULT_RATE_TYPE,
            ~FclFreightRate.rate_not_available_entry).first()
    return fcl_freight_rate_data


def is_weight_limit_verified(fcl_freight_rate_data):
    weight_limit = fcl_freight_rate_data.weight_limit
    if not weight_limit:
        return ' weight limit not present,'
    if (not weight_limit['free_limit']):
        return ' overweight weight surcharge free limit is not present,'
    if (not weight_limit['slabs']):
        return ' weight limit slabs is not present,'

    return ''
