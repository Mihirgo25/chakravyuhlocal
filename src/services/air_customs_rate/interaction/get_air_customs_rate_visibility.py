
from database.rails_db import get_organization, get_eligible_orgs
from services.air_customs_rate.models.air_customs_rate import AirCustomsRate

def get_air_customs_rate_visibility(request):
    response_object = { 'reason': '', 'is_rate_available': False, 'is_visible': False }
    org_services = []
    org_details = get_organization(id=request.get('service_provider_id'), account_type = 'service_provider')
    if org_details:
        org_details = org_details[0]
        org_services = get_eligible_orgs(None, str(org_details.get('id') or ''))

    kyc_and_service_status = is_kyc_verified_and_service_validation_status(org_details, org_services)
    if kyc_and_service_status:
        response_object['reason'] += kyc_and_service_status

    air_customs_rate_data = get_air_customs_rate_data(request)

    response_object['is_visible'] = not response_object['reason']
    response_object['is_rate_available'] = True if air_customs_rate_data else False
    return response_object

def is_kyc_verified_and_service_validation_status(org_details, org_services):
    kyc_and_service_reason = ''
    if not org_details:
        kyc_and_service_reason += ' service provider not present'
    if org_details and org_details.get('kyc_status') != 'verified':
        kyc_and_service_reason += f" kyc status is {org_details['kyc_status'].replace('_' , ' ')},"
    if org_details and org_details.get('status') == 'inactive':
        kyc_and_service_reason += ' service provider status is inactive,'
    if (not org_services) or 'air_customs' not in org_services:
        kyc_and_service_reason += ' air custom service is not activated for the organization,'

    return kyc_and_service_reason

def get_air_customs_rate_data(request):
    air_customs_rate_data = None

    if request.get('rate_id'):
        air_customs_rate_data = AirCustomsRate.select().where(AirCustomsRate.id == request['rate_id']).first()
    else:
        air_customs_rate_data = AirCustomsRate.select(AirCustomsRate.id).where(
            AirCustomsRate.airport_id == request.get('location_id'),
            AirCustomsRate.commodity == request.get('commodity'),
            AirCustomsRate.service_provider_id == request.get('service_provider_id'),
            ~AirCustomsRate.rate_not_available_entry).first()
    return air_customs_rate_data