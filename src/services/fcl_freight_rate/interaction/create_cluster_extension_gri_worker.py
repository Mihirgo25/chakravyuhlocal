from services.fcl_freight_rate.models.cluster_extension_gri_worker import ClusterExtensionGriWorker
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects

def create_cluster_extension_gri_worker(request):
    worker_object = create_or_update_worker(request)
    
    return {'id': worker_object.id, 'status': 'created'}

def create_or_update_worker(request_data):
 
    worker_data = {
        'container_type': request_data['container_type'],
        'container_size': request_data['container_size'],
        'origin_port_id': request_data['origin_port_id'],
        'destination_port_id': request_data['destination_port_id'],
        'min_decrease_percent': request_data['min_decrease_percent'],
        'max_increase_percent': request_data['max_increase_percent'],
        'min_decrease_amount': request_data['min_decrease_percent'],
        'max_increase_amount': request_data['max_increase_percent'],
        'manual_gri':request_data['manual_gri'],
        'commodity': 'general',
        'status': 'done',
        'performed_by_id': request_data.get('performed_by_id'),
        'performed_by_type': request_data.get('performed_by_type')
    }
    
    new_worker_object = ClusterExtensionGriWorker(**worker_data)    
    get_multiple_service_objects(new_worker_object)
    new_worker_object.set_locations()
    new_worker_object.save()
    
    return new_worker_object
