from database.rails_db import get_service_provider,get_shipping_line,get_user

def get_multiple_service_objects(freight_object):
    if hasattr(freight_object,'shipping_line_id'):  
        shipping_line = get_shipping_line(freight_object.shipping_line_id)
        shipping_line[0]['id'] = str(shipping_line[0]['id'])
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
    user_data = get_user(user_list)
    for user in user_data:
        user['id'] = str(user['id'])
        if user['id']==str(freight_object.procured_by_id):
            freight_object.procured_by= user        
        elif user['id']== str(freight_object.sourced_by):
            freight_object.sourced_by= user
        elif hasattr(freight_object,'performed_by_id') and user['id']==str(freight_object.performed_by_id):
            freight_object.performed_by_id = user        
        elif hasattr(freight_object,'closed_by_id') and user['id']==str(freight_object.closed_by_id):
            freight_object.closed_by_id = user    
    organization_list=[]
    if hasattr(freight_object,'importer_exporter_id'):
        organization_list.append(freight_object.importer_exporter_id)
    if hasattr(freight_object,'service_provider_id'):
        organization_list.append(freight_object.service_provider_id)
    organization_data = get_service_provider(organization_list)
    for organization in organization_data:
        organization['id']= str(organization['id'])
        if organization['id']==str(freight_object.service_provider_id):
            freight_object.service_provider = organization       
        else:
         freight_object.importer_exporter= organization    

    # if hasattr(freight_object,'rate_sheet_id'):
    #     rate_sheet_data = RateSheet.select(RateSheet.serial_id,RateSheet.file_name,RateSheet.created_at,RateSheet.updated_at).dicts().get()
    #     rate_sheet_data['serial_id'] = str(rate_sheet_data['serial_id'])
    #     freight_object.rate_sheet = rate_sheet_data    

    # if hasattr(freight_object,'spot_search_id'):
    #     sport_search_data = SpotSearch.select(SpotSearch.id,SpotSearch.importer_exporter_id,SpotSearch.importer_exporter,SpotSearch.service_details).dicts().get()
    #     sport_search_data['id']= str(sport_search_data['id'])
    #     sport_search_data['importer_exporter_id'] = str(sport_search_data['importer_exporter_id'])
    freight_object.save()


