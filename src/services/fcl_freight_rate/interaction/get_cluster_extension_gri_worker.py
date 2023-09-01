from datetime import datetime, timedelta
from services.fcl_freight_rate.models.cluster_extension_gri_worker import ClusterExtensionGriWorker
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.bramhastra.interactions.list_fcl_freight_rate_statistics import list_fcl_freight_rate_statistics
from services.fcl_freight_rate.helpers.rate_extension_via_bulk_operation import rate_extension_via_bulk_operation

MAIN_SHIPPING_LINE_IDS = []

def get_filters(start_time, query_type, rate_ids, shipping_line_ids):
    filters = {
        "updated_at_less_than": start_time,
        "query_type": query_type,
        "rate_id": rate_ids,
        "shipping_line_id": shipping_line_ids,
        "group_by": "shipping_line_id"
    }
    return filters
    

async def get_cluster_extension_gri_worker(request):
    today = request.get("start_time")
    
    origin_port_id = request["origin_port_id"]
    destination_port_id = request["destination_port_id"]
    container_type = request["container_type"]
    commodity = request["commodity"]
    
    query = ClusterExtensionGriWorker.select().where(
        (ClusterExtensionGriWorker.origin_port_id == origin_port_id) &
        (ClusterExtensionGriWorker.destination_port_id == destination_port_id) &
        (ClusterExtensionGriWorker.container_type == container_type) &
        (ClusterExtensionGriWorker.commodity == commodity) &
        (ClusterExtensionGriWorker.container_size.in_([20, 40]))
    )

    container_ranges = {"20": (-5, 10), "40": (-5, 10)}
    
    for row in list(query.dicts()):
        container_ranges[row["container_size"]] = (row["min_range"], row["max_range"]) ;

    for container_size in ["20", "40", "40HC"]:
        min_range, max_range = container_ranges["40"] if container_size == "40HC" else container_ranges[container_size]

        start_cur, end_cur = today - timedelta(hours=6), today
        
        query = (FclFreightRate
                .select(FclFreightRate.id, FclFreightRate.shipping_line_id, FclFreightRate.validities) 
                .where(
                    (FclFreightRate.updated_at > start_cur) &
                    (FclFreightRate.updated_at < end_cur) &
                    (FclFreightRate.origin_port_id == origin_port_id) &
                    (FclFreightRate.destination_port_id == destination_port_id)
                ))  
        
        rate_ids = []
        shipping_line_ids = []

        records = query.execute()
        for record in records:
            rate_ids.append(str(record.id)) 
            shipping_line_ids.append(record.shipping_line_id)
        

        response = await list_fcl_freight_rate_statistics(get_filters(start_cur, "average_price", rate_ids, shipping_line_ids), 1, 1, False)
        
        overall_gri_avg = 0
        
        UPDATED_SHIPPING_LINES = []
        for id in response[0]:
            if response[0][id] is not None and response[1][id] is not None:
                UPDATED_SHIPPING_LINES.append(id)
                aa = response[0][id]
                bb = response[1][id]
                perc = ((aa - bb) / aa) * 100
                overall_gri_avg += perc
                

        overall_gri_avg /= len(UPDATED_SHIPPING_LINES)
        
        TO_BE_UPDATED_SHIPPING_LINES = [id for id in MAIN_SHIPPING_LINE_IDS if id not in UPDATED_SHIPPING_LINES]
        
        if min_range <= overall_gri_avg <= max_range:
            request["markup"] = overall_gri_avg
            request["shipping_line_id"] = TO_BE_UPDATED_SHIPPING_LINES
            request["container_size"] = container_size
            
            rate_extension_via_bulk_operation(request)

            request.pop('shipping_line_id')
            request['origin_port_id']+= 
            request['destination_port_id']+= 

            
            rate_extension_via_bulk_operation(request)
            
                      
