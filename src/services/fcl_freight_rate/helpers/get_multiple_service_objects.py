from micro_services.client import *
from database.rails_db import get_organization,get_operators,get_user

def get_multiple_service_objects(freight_object, is_new_rate=True):
    if is_new_rate and hasattr(freight_object,'shipping_line_id') and freight_object.shipping_line_id:
        shipping_line = get_operators(id=str(freight_object.shipping_line_id))
        if len(shipping_line or []) > 0:
            try:
                freight_object.shipping_line = shipping_line[0]
            except:
                freight_object.shipping_line_detail = shipping_line[0]

    if is_new_rate and hasattr(freight_object,'airline_id') and freight_object.airline_id and not freight_object.airline :
        airline = get_operators(id=str(freight_object.airline_id))
        if len(airline or []) > 0:
            try:
                freight_object.airline = airline[0]
            except:
                freight_object.airline_detail = airline[0]
    
        
            
    user_list =[]
    if hasattr(freight_object,'procured_by_id') and freight_object.procured_by_id:
        user_list.append(freight_object.procured_by_id)
    if hasattr(freight_object,'sourced_by_id') and freight_object.sourced_by_id:
        user_list.append(freight_object.sourced_by_id)
    if hasattr(freight_object,'performed_by_id') and freight_object.performed_by_id:
        user_list.append(freight_object.performed_by_id)
    if hasattr(freight_object,'closed_by_id') and freight_object.closed_by_id:
        user_list.append(freight_object.closed_by_id)
    if hasattr(freight_object,'completed_by_id'):
        user_list.append(freight_object.completed_by_id)

    if user_list:
        user_data = get_user(user_list)
        for user in user_data:
            if hasattr(freight_object,'procured_by_id') and user['id']==str(freight_object.procured_by_id):
                freight_object.procured_by= user
            if hasattr(freight_object,'sourced_by_id') and user['id']== str(freight_object.sourced_by_id):
                freight_object.sourced_by= user
            if hasattr(freight_object,'performed_by_id') and user['id']==str(freight_object.performed_by_id):
                freight_object.performed_by = user
            if hasattr(freight_object,'closed_by_id') and user['id']==str(freight_object.closed_by_id):
                freight_object.closed_by = user
            if hasattr(freight_object,'completed_by_id') and user['id']==str(freight_object.completed_by_id):
                freight_object.completed_by = user
    organization_list=[]
    if hasattr(freight_object,'importer_exporter_id') and freight_object.importer_exporter_id :
        organization_list.append(freight_object.importer_exporter_id)
    if is_new_rate and hasattr(freight_object,'service_provider_id') and freight_object.service_provider_id and not freight_object.service_provider:
        organization_list.append(freight_object.service_provider_id)
    if hasattr(freight_object,'performed_by_org_id') and freight_object.performed_by_org_id:
        organization_list.append(freight_object.performed_by_org_id)
    if organization_list:
        organization_data = get_organization(id=organization_list)
        for organization in organization_data:
            if is_new_rate and hasattr(freight_object,'service_provider_id') and not freight_object.service_provider and organization['id']==str(freight_object.service_provider_id):
                freight_object.service_provider = organization
            if hasattr(freight_object,'importer_exporter_id') and organization['id']==str(freight_object.importer_exporter_id):
                freight_object.importer_exporter= organization
            if hasattr(freight_object,'performed_by_org_id') and organization['id']==str(freight_object.performed_by_org_id):
                if hasattr(freight_object,'organization'):
                    freight_object.organization = organization
                elif hasattr(freight_object,'performed_by_org'):
                    freight_object.performed_by_org = organization

    # if hasattr(freight_object,'rate_sheet_id'):
    #     rate_sheet_data = RateSheet.select(RateSheet.serial_id,RateSheet.file_name,RateSheet.created_at,RateSheet.updated_at).dicts().get()
    #     rate_sheet_data['serial_id'] = str(rate_sheet_data['serial_id'])
    #     freight_object.rate_sheet = rate_sheet_data


    freight_object.save()

