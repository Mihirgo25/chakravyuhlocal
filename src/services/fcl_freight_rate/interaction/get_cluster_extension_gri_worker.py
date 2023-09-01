from datetime import datetime, timedelta
from services.fcl_freight_rate.models.cluster_extension_gri_worker import ClusterExtensionGriWorker
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.bramhastra.interactions.list_fcl_freight_rate_statistics import list_fcl_freight_rate_statistics
from services.fcl_freight_rate.helpers.rate_extension_via_bulk_operation import rate_extension_via_bulk_operation
from micro_services.client import common
from services.fcl_freight_rate.models.fcl_freight_location_cluster import FclFreightLocationCluster
from services.fcl_freight_rate.models.fcl_freight_location_cluster_mapping import FclFreightLocationClusterMapping

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
        
        records = query.execute()
        
        
        prices = []
        rate_ids = []
        shipping_line_ids = []
        
        for record in records:
            rate_ids.append(str(record.id)) 
            shipping_line_ids.append(str(record.shipping_line_id))
            
            price = 0
            for validity in record.validities:
                if validity["currency"] != "USD":
                    data = {
                        "from_currency" : validity["currency"],
                        "to_currency": "USD",
                        "price": validity["price"]
                    }                    
                    price_in_USD = common.get_money_exchange_for_fcl(data)["price"]
                    price += price_in_USD
                else:
                    price += validity["price"]
                    
            prices.append(price)       
                
      
        # ? what will be the format of response. (considered dictionary here)
        # * going to get average for each unique shipping line
        response = await list_fcl_freight_rate_statistics(get_filters(start_cur, "average_price", rate_ids, shipping_line_ids), 1, 1, False)
        
        
        
        # * grouping of shipping_line_id to get average prices for each unique shipping_line_id
        shipping_line_totals = {}
        shipping_line_counts = {}

        for shipping_id, price in zip(shipping_line_ids, prices):
            if shipping_id not in shipping_line_totals:
                shipping_line_totals[shipping_id] = price
                shipping_line_counts[shipping_id] = 1
            else:
                shipping_line_totals[shipping_id] += price
                shipping_line_counts[shipping_id] += 1

        average_prices = {} # * for each shipping line
        for shipping_id in shipping_line_totals:
            total = shipping_line_totals[shipping_id]
            count = shipping_line_counts[shipping_id]
            average_prices[shipping_id] = total / count 
            
        overall_gri_avg = 0
        
    
        # * calculating overall_gri_avg and getting UPDATED_SHIPPING_LINES
        UPDATED_SHIPPING_LINES = []
        for shipping_line in average_prices.keys(): 
            UPDATED_SHIPPING_LINES.append(shipping_line)
            cur = average_prices[shipping_line]
            prev = response[shipping_line]
            
            overall_gri_avg += ((cur - prev) / cur) * 100  
            
        overall_gri_avg /= len(average_prices)
        
        
        
        # * TMAIN_SHIPPING_LINE is empty
        TO_BE_UPDATED_SHIPPING_LINES = [id for id in MAIN_SHIPPING_LINE_IDS if id not in UPDATED_SHIPPING_LINES]
        
        
        # * location_ids for origin_port_id
        cluster_id_origin = FclFreightLocationCluster.get(FclFreightLocationCluster.base_port_id == request["origin_port_id"]).id
        
        
        query = (FclFreightLocationClusterMapping
                .select(FclFreightLocationClusterMapping.location_id)
                .where(FclFreightLocationClusterMapping.cluster_id == cluster_id_origin))      
        
        records = query.execute()  
        
        ports_for_base_origin_port_id = [record.location_id for record in records]
        
        
        
        
        # * location_ids for destination_port_id
        cluster_id_destination = FclFreightLocationCluster.get(FclFreightLocationCluster.base_port_id == request["destination_port_id"]).id
        
        query = (FclFreightLocationClusterMapping
                .select(FclFreightLocationClusterMapping.location_id)
                .where(FclFreightLocationClusterMapping.cluster_id == cluster_id_destination))      
        
        records = query.execute()  
        
        ports_for_destination_port_id = [record.location_id for record in records]    
        
        
        # * Performing bulk operations
        if min_range <= overall_gri_avg <= max_range:
            request["markup"] = overall_gri_avg
            request["shipping_line_id"] = TO_BE_UPDATED_SHIPPING_LINES
            request["container_size"] = container_size
            
            rate_extension_via_bulk_operation(request)

            request.pop('shipping_line_id')
            request['origin_port_id'] = ports_for_base_origin_port_id
            request['destination_port_id'] = ports_for_destination_port_id

            rate_extension_via_bulk_operation(request)
            
