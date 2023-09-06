from services.fcl_freight_rate.models.cluster_extension_gri_worker import ClusterExtensionGriWorker
from services.fcl_freight_rate.helpers.get_multiple_service_objects import get_multiple_service_objects
from database.db_session import db

def create_critical_port_trend_index(request):
    with db.atomic():
        return execute_transaction_code(request)


def execute_transaction_code(request_data):
    create_params = {
        "origin_port_id": request_data["origin_port_id"],
        "destination_port_id": request_data["destination_port_id"],
        "min_decrease_percent": request_data["min_decrease_percent"],
        "max_increase_percent": request_data["max_increase_percent"],
        "min_decrease_markup": request_data["min_decrease_percent"],
        "max_increase_markup": request_data["max_increase_percent"],
        "manual_gri": request_data.get("manual_gri"),
        "approval_status": request_data.get("approval_status"),
        "performed_by_id": request_data.get("performed_by_id"),
        "performed_by_type": request_data.get("performed_by_type"),
    }

    new_worker_object = ClusterExtensionGriWorker(**create_params)
    get_multiple_service_objects(new_worker_object)
    new_worker_object.set_locations()
    new_worker_object.save()

    return {id: str(new_worker_object.id)}
