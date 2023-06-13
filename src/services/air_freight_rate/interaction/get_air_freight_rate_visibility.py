from services.air_freight_rate.models.air_freight_rate import AirFreightRate
from database.rails_db import get_organization
from micro_services.client import organization

def get_air_freight_rate_visibility(request):
    response_object = {'reason': '', 'is_rate_available': False, 'is_visible': False }

    org_details = get_organization(id = request['service_provider_id'],account_type = 'service_provider')[0]
    
    org_services_data = organization.list_organization_services({'filters':{'organization_id' : str(org_details['id']), 'status' : 'active'}})
    
    if 'list' in org_services_data:
            org_services_data = org_services_data['list']
    else:
        org_services_data = []
    org_services = [service['service'] for service in org_services_data]
    
    kyc_and_service_status = is_kyc_verified_and_service_validation_status(org_details, org_services)
    
    if kyc_and_service_status:
        response_object['reason'] += kyc_and_service_status

    air_freight_rate_data=get_air_freght_rate_data(request)
    
    if (not air_freight_rate_data) or ((not request.get('from_date')) or (not request.get('to_date'))):
        response_object['is_visible'] = False
        if (not request.get('from_date')) or (not request.get('to_date')):
            response_object['is_visible'] = False
        return response_object
    
    response_object['is_visible'] = not response_object['reason']
    response_object['is_rate_available'] = True if air_freight_rate_data else False
    return response_object

def is_kyc_verified_and_service_validation_status(org_details,org_services):
    
    kyc_and_service_reason = ''
    if not org_details:
        kyc_and_service_reason += ' service provider not present'
    if org_details and org_details['kyc_status'] != 'verified':
        kyc_and_service_reason += f" kyc status is f{org_details['kyc_status'].replace('_' , ' ')},"
    if org_details and org_details['status'] == 'inactive':
        kyc_and_service_reason += ' air service provider status is inactive,'
    if (not org_services) or 'air_freight' not in org_services:
        kyc_and_service_reason += ' air service is not activated for the organization,'

    return kyc_and_service_reason


def get_air_freght_rate_data(request):
    air_freight_rate_data = None
    if request.get('rate_id'):
        air_freight_rate_data = AirFreightRate.select().where(AirFreightRate.id == request['rate_id']).first()
    else:
        air_freight_rate_data = AirFreightRate.select().where(
            AirFreightRate.origin_airport_id  == request['origin_location_id'],
            AirFreightRate.destination_airport_id == request['destination_location_id'],
            AirFreightRate.service_provider_id  ==  request['service_provider_id'],
            AirFreightRate.commodity  ==  request['commodity'],
            AirFreightRate.airline_id  ==  request['airline_id'],
            ~AirFreightRate.rate_not_available_entry).first()
        
    return air_freight_rate_data
    


