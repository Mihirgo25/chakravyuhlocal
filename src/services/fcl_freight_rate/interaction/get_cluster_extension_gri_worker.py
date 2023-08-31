from datetime import datetime, timedelta
from services.fcl_freight_rate.models.cluster_extension_gri_worker import ClusterExtensionGriWorker
from services.bramhastra.interactions.list_fcl_freight_rate_statistics import list_fcl_freight_rate_statistics
from services.fcl_freight_rate.helpers.rate_extension_via_bulk_operation import rate_extension_via_bulk_operation


def get_filters(request, start_time, end_time, query_type, container_size):
    filters = {
        "start_time": start_time, 
        "end_time": end_time,
        "origin_port_id": request["origin_port_id"],
        "destination_port_id":request["destination_port_id"],
        "query_type": query_type,
        "container_size": container_size
    }
    return filters
    

async def get_cluster_extension_gri_worker(request):
    today = request.get("start_time")
    origin_port_id = request["origin_port_id"]
    destination_port_id = request["destination_port_id"]
    container_type = request["container_type"]

    query = ClusterExtensionGriWorker.select().where(
        (ClusterExtensionGriWorker.origin_port_id == origin_port_id) &
        (ClusterExtensionGriWorker.destination_port_id == destination_port_id) &
        (ClusterExtensionGriWorker.container_type == container_type) &
        (ClusterExtensionGriWorker.container_size.in_([20, 40]))
    )

    container_ranges = {'20': (-5, 10), '40': (-5, 10)}
    for row in list(query.dicts()):
        container_ranges[row["container_size"]] = (row["min_range"], row["max_range"]) ;

    for container_size in ['20', '40', '40HC']:
        min_range, max_range = container_ranges['40'] if container_size == '40HC' else container_ranges[container_size]

        start_cur, end_cur = today - timedelta(hours=6), today
        start_prev, end_prev = today - timedelta(hours=12), today - timedelta(hours=6)
        
        current_response = await list_fcl_freight_rate_statistics(get_filters(request, start_cur, end_cur, "average_price", container_size), 1, 1, False)
        
        previous_response = await list_fcl_freight_rate_statistics(get_filters(request, start_prev, end_prev, "average_price", container_size), 1, 1, False)
        
        current_avg = current_response["list"][0]["average_standard_price"]
        
        previous_avg = previous_response["list"][0]["average_standard_price"]
        
        gri_percentage = ((current_avg - previous_avg) / current_avg) * 100

        if min_range <= gri_percentage <= max_range:
            request["markup"] = gri_percentage
            request["container_size"] = container_size
        
            rate_extension_via_bulk_operation(request)

