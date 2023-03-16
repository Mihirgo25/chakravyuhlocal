
from rails_client import client
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate

def get_multiple_service_objects(freight_object,service_objects):
    client.initialize_client()
    data = client.ruby.get_multiple_service_objects_data_for_fcl(service_objects)
    print(data)
    freight_object.shipping_line = data['operator'][str(freight_object.shipping_line_id)]
    freight_object.procured_by = data['user'][str(freight_object.procured_by_id)]
    freight_object.sourced_by = data['user'][str(freight_object.sourced_by_id)]
    freight_object.service_provider = data['organization'][str(freight_object.service_provider_id)]
    freight_object.importer_exporter = data['organization'][str(freight_object.importer_exporter_id)]
    freight_object.save()

    return data
        
