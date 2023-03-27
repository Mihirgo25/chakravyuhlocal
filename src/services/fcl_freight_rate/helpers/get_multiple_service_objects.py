from peewee import fn
from micro_services.client import *
from database.rails_db import get_service_provider,get_shipping_line,get_user

def get_multiple_service_objects(freight_object):
    if hasattr(freight_object,'shipping_line_id'):  
        shipping_line = get_shipping_line(freight_object.shipping_line_id)
        freight_object.shipping_line = shipping_line[0]  
    user_list =[]
    if hasattr(freight_object,'procured_by_id'):
        user_list.append(freight_object.procured_by_id)
    if hasattr(freight_object,'sourced_by_id'):
        user_list.append(freight_object.sourced_by_id)
    if hasattr(freight_object,'performed_by_id'):
        user_list.append(freight_object.performed_by_id)
    if hasattr(freight_object,'closed_by_id'):
        user_list.append(freight_object.closed_by_id)

    if user_list:
        user_data = get_user(user_list)
        for user in user_data:
            if hasattr(freight_object,'procured_by_id') and user['id']==str(freight_object.procured_by_id):
                freight_object.procured_by= user        
            elif hasattr(freight_object,'sourced_by_id') and user['id']== str(freight_object.sourced_by_id):
                freight_object.sourced_by= user
            elif hasattr(freight_object,'performed_by_id') and user['id']==str(freight_object.performed_by_id):
                freight_object.performed_by = user        
            elif hasattr(freight_object,'closed_by_id') and user['id']==str(freight_object.closed_by_id):
                freight_object.closed_by = user    
            elif hasattr(freight_object,'completed_by_id') and user['id']==str(freight_object.completed_by_id):
                freight_object.completed_by = user
    organization_list=[]
    if hasattr(freight_object,'importer_exporter_id'):
        organization_list.append(freight_object.importer_exporter_id)
    if hasattr(freight_object,'service_provider_id'):
        organization_list.append(freight_object.service_provider_id)
    if hasattr(freight_object,'performed_by_org_id'):
        user_list.append(freight_object.performed_by_org_id)
    if organization_list:
        organization_data = get_service_provider(organization_list)
        for organization in organization_data:
            if hasattr(freight_object,'service_provider_id') and organization['id']==str(freight_object.service_provider_id):
                freight_object.service_provider = organization       
            if hasattr(freight_object,'importer_exporter_id') and organization['id']==str(freight_object.importer_exporter_id):
                freight_object.importer_exporter= organization
            if hasattr(freight_object,'performed_by_org_id') and organization['id']==str(freight_object.performed_by_org_id):
                freight_object.organization = organization

    # if hasattr(freight_object,'rate_sheet_id'):
    #     rate_sheet_data = RateSheet.select(RateSheet.serial_id,RateSheet.file_name,RateSheet.created_at,RateSheet.updated_at).dicts().get()
    #     rate_sheet_data['serial_id'] = str(rate_sheet_data['serial_id'])
    #     freight_object.rate_sheet = rate_sheet_data    

    if hasattr(freight_object,'source_id'):
        spot_search_data = common.list_spot_searches({'filters':{'id':str(freight_object.source_id)}})
        if spot_search_data:
            spot_search_data = spot_search_data['list'][0]
            freight_object.spot_search = {key:value for key,value in spot_search_data.items() if key in ['id','importer_exporter_id','importer_exporter','service_details']}
            
    freight_object.save()
