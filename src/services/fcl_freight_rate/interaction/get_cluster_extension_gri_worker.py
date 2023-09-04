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
    return {
        "updated_at_less_than": start_time,
        "query_type": query_type,
        "rate_id": rate_ids,
        "shipping_line_id": shipping_line_ids,
        "group_by": "shipping_line_id"
    }
    
def get_shipping_line_dict():
    return {
        "20": None,
        "40": None,
        "40HC": None
    }

async def get_cluster_extension_gri_worker(request):
    today = request.get("start_time")
    
    origin_port_id = request["origin_port_id"]
    destination_port_id = request["destination_port_id"]
    
    min_range, max_range = -5, 10
    
    query = (ClusterExtensionGriWorker
            .select(ClusterExtensionGriWorker.min_range, ClusterExtensionGriWorker.max_range)
            .where((ClusterExtensionGriWorker.destination_port_id == destination_port_id) &
            (ClusterExtensionGriWorker.origin_port_id == origin_port_id)))

    
    record = query.get()

    if record:
        min_range = record.min_range
        max_range = record.max_range

        
    shipping_line_gri_mapping = {}
    
    for container_size in ["20", "40", "40HC"]:
    
        start_time, end_time = today - timedelta(hours = 6), today

        query = (FclFreightRate
                .select(FclFreightRate.id, FclFreightRate.shipping_line_id, FclFreightRate.validities) 
                .where(
                    FclFreightRate.updated_at > start_time,
                    FclFreightRate.updated_at < end_time,
                    FclFreightRate.origin_port_id == origin_port_id,
                    FclFreightRate.destination_port_id == destination_port_id,
                    FclFreightRate.container_size == container_size
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
                            
            
                
        # * standard_average_price for each unique shipping line
        response = await list_fcl_freight_rate_statistics(get_filters(start_time, "average_price", rate_ids, shipping_line_ids), 1, 1, False)
        
        
        
        # * average price for each shipping_line_id (groupby shipping_line_id)
        shipping_line_totals = {}
        shipping_line_counts = {}

        for shipping_id, price in zip(shipping_line_ids, prices):
            if shipping_id not in shipping_line_totals:
                shipping_line_totals[shipping_id] = price
                shipping_line_counts[shipping_id] = 1
            else:
                shipping_line_totals[shipping_id] += price
                shipping_line_counts[shipping_id] += 1

        average_prices = {}
        for shipping_id in shipping_line_totals:
            total = shipping_line_totals[shipping_id]
            count = shipping_line_counts[shipping_id]
            average_prices[shipping_id] = total / count 
            
        # * shipping_line_id gri percentage mapping
        for shipping_line_id in average_prices.keys(): 
            cur = average_prices[shipping_line_id]
            prev = response[shipping_line_id]
            
            if prev and cur:
                gri_perc = ((cur - prev) / cur) * 100 
                if shipping_line_id in shipping_line_gri_mapping.keys():
                    shipping_line_gri_mapping[shipping_line_id][container_size] = gri_perc
                else:
                    shipping_line_gri_mapping[shipping_line_id] = get_shipping_line_dict()
                    shipping_line_gri_mapping[shipping_line_id][container_size] = gri_perc
                    
    
    shipping_line_avg_mapping = {}

    for key, sub_dict in shipping_line_gri_mapping.items():
        values = []
        for sub_key in sub_dict:
            if sub_key in {"20", "40", "40HC"}: 
                values.append(sub_dict[sub_key])
        if values:  
            average_value = sum(values) / len(values)
            shipping_line_avg_mapping[key] = average_value
            
    
    overall_gri_avg = 0  
    for key in shipping_line_avg_mapping.keys():
        overall_gri_avg += shipping_line_avg_mapping[key]
    
    overall_gri_avg /= len(shipping_line_avg_mapping)
    
    
    UPDATED_SHIPPING_LINES = shipping_line_gri_mapping.keys()
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
    
    # ? how to calculate overall_gri for performing bulk operations
     # * what i understands
     # * taking average of "20", "40" and "40HC" for each shipping_line_id and 
     # * then taking average of average calculated for each shipping_line_id
    # ? from which table we'll get min_range and max_range and on what basis
    
    if min_range <= overall_gri_avg <= max_range:
        request["markup"] = overall_gri_avg
        request["shipping_line_id"] = TO_BE_UPDATED_SHIPPING_LINES
        # * request["container_size"] = container_size
        
        rate_extension_via_bulk_operation(request)

        request.pop('shipping_line_id')
        request['origin_port_id'] = ports_for_base_origin_port_id
        request['destination_port_id'] = ports_for_destination_port_id

        rate_extension_via_bulk_operation(request)
        
