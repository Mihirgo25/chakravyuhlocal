from database.rails_db import get_organization
from micro_services.client import organization
from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate

def get_fcl_customs_rate_visibility(request):
    response_object = { 'reason': '', 'is_rate_available': False, 'is_visible': False }
    org_services = []
    org_details = get_organization(id=request['service_provider_id'])
    if org_details:
        org_details = org_details[0]
        org_services_data = organization.list_organization_services({'filters':{'organization_id' : str(org_details['id']), 'status' : 'active'}})
        if org_services_data:
            org_services_data = org_services_data['list']
        else:
            org_services_data = []
        org_services = [service['service'] for service in org_services_data]

    kyc_and_service_status = is_kyc_verified_and_service_validation_status(org_details, org_services)
    if kyc_and_service_status:
        response_object['reason'] += kyc_and_service_status

    fcl_customs_rate_data = get_fcl_customs_rate_data(request)

    response_object['is_visible'] = not response_object['reason']
    response_object['is_rate_available'] = True if fcl_customs_rate_data else False
    return response_object

def is_kyc_verified_and_service_validation_status(org_details, org_services):
    kyc_and_service_reason = ''
    if not org_details:
        kyc_and_service_reason += ' service provider not present'
    if org_details and org_details.get('kyc_status') != 'verified':
        kyc_and_service_reason += f" kyc status is {org_details['kyc_status'].replace('_' , ' ')},"
    if org_details and org_details.get('status') == 'inactive':
        kyc_and_service_reason += ' service provider status is inactive,'
    if (not org_services) or 'fcl_customs' not in org_services:
        kyc_and_service_reason += ' fcl customs is not activated for the organization,'

    return kyc_and_service_reason

def get_fcl_customs_rate_data(request):
    fcl_customs_rate_data = None

    if request.get('rate_id'):
        fcl_customs_rate_data = FclCustomsRate.select().where(FclCustomsRate.id == request['rate_id']).first()
    else:
        fcl_customs_rate_data = FclCustomsRate.select().where(
            FclCustomsRate.location_id == request.get('location_id'),
            FclCustomsRate.container_size == request.get('container_size'),
            FclCustomsRate.container_type == request.get('container_type'),
            FclCustomsRate.commodity == request.get('commodity'),
            FclCustomsRate.service_provider_id == request.get('service_provider_id'),
            ~FclCustomsRate.rate_not_available_entry).first()
    return fcl_customs_rate_data