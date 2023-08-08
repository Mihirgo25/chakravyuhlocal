from services.haulage_freight_rate.models.haulage_freight_rate import HaulageFreightRate
from database.rails_db import get_organization
from micro_services.client import organization


def get_haulage_freight_rate_visibility(request):
    """
    Get Haulage Freight Rate Visibility
    Response Format:
        {
        reason: reason why its not visible,
        is_rate_available: True,
        is_visible: True,
        }
    """
     
    response_object = {'reason': '', 'is_rate_available': False, 'is_visible': False }
    org_details = None
    organizations = get_organization(id=request.get('service_provider_id'),account_type = 'service_provider')
    if organizations:
        org_details = organizations[0]
    org_services_data = organization.list_organization_services({'filters':{'organization_id' : str(org_details['id']), 'status' : 'active'}})
    if org_services_data.get('list'):
        org_services_data = org_services_data['list']
    else:
        org_services_data = []
    org_services = [service['service'] for service in org_services_data]
    kyc_and_service_status = is_kyc_verified_and_service_validation_status(org_details, org_services)

    if kyc_and_service_status:
        response_object['reason'] += kyc_and_service_status

    haulage_freight_rate_data = get_haulage_freight_rate_data(request)

    response_object['is_visible'] = not response_object['reason']
    response_object['is_rate_available'] = True if haulage_freight_rate_data else False
    return response_object

def is_kyc_verified_and_service_validation_status(org_details, org_services):
    kyc_and_service_reason = ''
    if not org_details:
        kyc_and_service_reason += ' service provider not present'
    if org_details and org_details.get('kyc_status') != 'verified':
        kyc_and_service_reason += f" kyc status is {org_details.get('kyc_status').replace('_' , ' ')},"
    if org_details and org_details.get('status') == 'inactive':
        kyc_and_service_reason += ' service provider status is inactive,'
    if (not org_services) or ('haulage_freight' not in org_services and 'trailer_freight' not in org_services):
        kyc_and_service_reason += ' haulage service is not activated for the organization,'
    return kyc_and_service_reason

def get_haulage_freight_rate_data(request):
    haulage_freight_rate_data = None
    
    if request['rate_id']:
        haulage_freight_rate_data = HaulageFreightRate.select().where(HaulageFreightRate.id == request['rate_id']).first()
    else:
        haulage_freight_rate_data = HaulageFreightRate.select().where(
            HaulageFreightRate.id  == request['origin_location_id'],
            HaulageFreightRate.destination_location_id == request['destination_location_id'],
            HaulageFreightRate.container_size  ==  request['container_size'],
            HaulageFreightRate.container_type  ==  request['container_type'],
            HaulageFreightRate.commodity  ==  request['commodity'],
            HaulageFreightRate.service_provider_id  ==  request['service_provider_id']).first()
    return haulage_freight_rate_data
