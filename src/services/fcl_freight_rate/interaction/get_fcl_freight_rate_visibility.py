from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from datetime import datetime
from database.rails_db import *
from micro_services.client import *
from datetime import datetime

def get_fcl_freight_rate_visibility(request):
    if request['from_date']:
        request['from_date'] = datetime.strptime(request['from_date'], '%Y-%m-%d')
    
    if request['to_date']:
        request['to_date'] = datetime.strptime(request['to_date'], '%Y-%m-%d')

    response_object = {'reason': '', 'is_rate_available': False, 'is_visible': False }

    org_details = get_service_provider(request['service_provider_id'])[0]

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

    if fcl_freight_rate_data.origin_local or fcl_freight_rate_data.destination_local:
        detention_status = is_detention_verified(fcl_freight_rate_data)
        if detention_status:
            response_object['reason'] += detention_status 

        demurrage_status = is_demurrage_verified(fcl_freight_rate_data)
        if demurrage_status:
            response_object['reason'] += demurrage_status 
    else:
        response_object['reason'] += ' origin local and destination local not present,'

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
            FclFreightRate.rate_not_available_entry == False).first()
    return fcl_freight_rate_data


def is_detention_verified(fcl_freight_rate_data):
    detention_reason = ''

    if fcl_freight_rate_data.origin_local:
        origin_detention_data = fcl_freight_rate_data.origin_local.get('detention')
    
    if fcl_freight_rate_data.destination_local:
        destination_detention_data = fcl_freight_rate_data.destination_local.get('detention') 
    
    if origin_detention_data and (not origin_detention_data['free_limit']):
        detention_reason += ' origin detention does not exist,' 
    
    if destination_detention_data and (not destination_detention_data['free_limit']):
        detention_reason += ' destination detention does not exist,'
    return detention_reason


def is_demurrage_verified(fcl_freight_rate_data):
    demurrage_reason = ''
    
    if fcl_freight_rate_data.origin_local:
        origin_demurrage_data = fcl_freight_rate_data.origin_local.get('demurrage') 
    
    if fcl_freight_rate_data.destination_local:
        destination_demurrage_data = fcl_freight_rate_data.destination_local.get('demurrage') 
    
    if origin_demurrage_data and (not origin_demurrage_data['free_limit']):
        demurrage_reason += ' origin demurrage does not exist,' 
    
    if destination_demurrage_data and (not destination_demurrage_data['free_limit']):
        demurrage_reason += ' destination demurrage does not exist,' 

    return demurrage_reason


def is_weight_limit_verified(fcl_freight_rate_data):
    weight_limit = fcl_freight_rate_data.weight_limit
    if not weight_limit:
        return ' weight limit not present,' 
    if (not weight_limit['free_limit']):
        return ' overweight weight surcharge free limit is not present,' 
    if (not weight_limit['slabs']):
        return ' weight limit slabs is not present,'

    return ''