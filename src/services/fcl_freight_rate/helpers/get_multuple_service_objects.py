
from rails_client import client
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.user import User
from services.fcl_freight_rate.models.operator import Operator
from services.fcl_freight_rate.models.organization import Organization
from peewee import fn
def get_multiple_service_objects(freight_object):
    shipping_line = Operator.select(Operator.id,Operator.business_name,Operator.short_name,Operator.logo_url).where(Operator.id ==freight_object.shipping_line_id).dicts().get()
    shipping_line['id'] = str(shipping_line['id'])
    freight_object.shipping_line = shipping_line
    user_data = list(User.select(User.id,User.name,User.email).where(User.id <<(freight_object.procured_by_id,freight_object.sourced_by_id)).dicts())
    print(user_data)
    for user in user_data:
        user['id'] = str(user['id'])
        if user['id']==str(freight_object.procured_by_id):
            freight_object.procured_by= user
        else:
            freight_object.sourced_by= user
   
    try:
        freight_object.importer_exporter_id = freight_object.importer_exporter_id
    except:
        freight_object.importer_exporter_id=None
    organization_data = list(Organization.select(Organization.id,Organization.business_name,Organization.short_name).where(Organization.id<<(freight_object.service_provider_id,freight_object.importer_exporter_id)).dicts())
    for organization in organization_data:
        organization['id']= str(organization['id'])
        if organization['id']==str(freight_object.service_provider_id):
            freight_object.service_provider = organization
        else:
         freight_object.importer_exporter= organization
    
    freight_object.save()
        
