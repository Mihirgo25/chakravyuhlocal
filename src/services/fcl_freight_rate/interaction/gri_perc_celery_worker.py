from datetime import datetime, timedelta
from services.fcl_freight_rate.helpers.rate_extension_via_bulk_operation import rate_extension_via_bulk_operation
from services.fcl_freight_rate.models.cluster_extension_gri_worker import ClusterExtensionGriWorker


def gri_perc_celery_worker(request):
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

        cur = get_pair_port_price_average(start_cur, end_cur, origin_port_id, destination_port_id, container_size)
        
        prev = get_pair_port_price_average(start_prev, end_prev, origin_port_id, destination_port_id, container_size)
        
        gri = ((cur - prev) / cur) * 100

        if min_range <= gri <= max_range:
            request["markup"] = gri
            request["container_size"] = container_size
        
            rate_extension_via_bulk_operation(request)
