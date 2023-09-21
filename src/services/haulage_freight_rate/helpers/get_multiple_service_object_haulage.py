from micro_services.client import *
from database.rails_db import get_organization, get_operators, get_user, list_organization_users

def get_multiple_service_objects_haulage(haulage_freight_object, is_new_rate=True):
    if is_new_rate and hasattr(haulage_freight_object,'shipping_line_id') and haulage_freight_object.shipping_line_id:
        shipping_line = get_operators(id=str(haulage_freight_object.shipping_line_id))
        if len(shipping_line or []) > 0:
            haulage_freight_object.shipping_line = shipping_line[0]
        
    
    user_list =[]
    if hasattr(haulage_freight_object,'procured_by_id') and haulage_freight_object.procured_by_id:
        user_list.append(haulage_freight_object.procured_by_id)
    if hasattr(haulage_freight_object,'sourced_by_id') and haulage_freight_object.sourced_by_id:
        user_list.append(haulage_freight_object.sourced_by_id)

    if user_list:
        user_data = get_user(user_list)
        organization_data = list_organization_users(user_list)
        for user in user_data:
            if hasattr(haulage_freight_object,'procured_by_id') and user['id']==str(haulage_freight_object.procured_by_id):
                haulage_freight_object.procured_by= user
            if hasattr(haulage_freight_object,'sourced_by_id') and user['id']== str(haulage_freight_object.sourced_by_id):
                haulage_freight_object.sourced_by= user
        for user in organization_data:
            if hasattr(haulage_freight_object,'procured_by_id') and user['id']==str(haulage_freight_object.procured_by_id):
                haulage_freight_object.procured_by= user
            if hasattr(haulage_freight_object,'sourced_by_id') and user['id']== str(haulage_freight_object.sourced_by_id):
                haulage_freight_object.sourced_by= user

    organization_list=[]
    if is_new_rate and hasattr(haulage_freight_object,'service_provider_id') and haulage_freight_object.service_provider_id and (hasattr(haulage_freight_object,'service_provider') and not haulage_freight_object.service_provider):
        organization_list.append(haulage_freight_object.service_provider_id)
    if organization_list:
        organization_data = get_organization(id=organization_list)
        for organization in organization_data:
            if is_new_rate and hasattr(haulage_freight_object,'service_provider_id') and (hasattr(haulage_freight_object,'service_provider') and not haulage_freight_object.service_provider) and organization['id']==str(haulage_freight_object.service_provider_id):
                haulage_freight_object.service_provider = organization
    
    haulage_freight_object.save()

