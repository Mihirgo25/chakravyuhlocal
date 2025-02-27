from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from database.rails_db import get_organization
from micro_services.client import organization

def get_ftl_freight_rate_visibility(request):
    response_object = { 'reason': '', 'is_rate_available': False, 'is_visible': False }
    org_services = []
    org_details = get_organization(id=request.get('service_provider_id'))
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

    ftl_freight_rate_data = get_ftl_freight_rate_data(request)

    if (not ftl_freight_rate_data) or ((not request['from_date']) or (not request['to_date'])):
        response_object['is_visible'] = False
        if (not request['from_date']) or (not request['to_date']):
            response_object['is_visible'] = False
        return response_object

    response_object['is_visible'] = not response_object['reason']
    response_object['is_rate_available'] = True if ftl_freight_rate_data else False
    return response_object


def is_kyc_verified_and_service_validation_status(org_details, org_services):
    kyc_and_service_reason = ''
    if not org_details:
        kyc_and_service_reason += ' service provider not present'
    if org_details and org_details['kyc_status'] != 'verified':
        kyc_and_service_reason += f" kyc status is f{org_details['kyc_status'].replace('_' , ' ')},"
    if org_details and org_details['status'] == 'inactive':
        kyc_and_service_reason += ' service provider status is inactive,'
    if (not org_services) or 'ftl_freight' not in org_services:
        kyc_and_service_reason += ' ftl service is not activated for the organization,'

    return kyc_and_service_reason

def get_ftl_freight_rate_data(request):
    ftl_freight_rate_data = None

    if request['rate_id']:
        ftl_freight_rate_data = FtlFreightRate.select().where(FtlFreightRate.id == request['rate_id']).first()
    else:
        ftl_freight_rate_data = FtlFreightRate.select().where(
            FtlFreightRate.service_provider_id  ==  request['service_provider_id'],
            FtlFreightRate.origin_location_id  ==  request['origin_location_id'],
            FtlFreightRate.destination_location_id  ==  request['destination_location_id'],
            FtlFreightRate.truck_type  ==  request['truck_type'],
            FtlFreightRate.commodity  ==  request['commodity'],
            ).first()
    return ftl_freight_rate_data
