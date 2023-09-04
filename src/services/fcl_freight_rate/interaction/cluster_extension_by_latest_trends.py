from datetime import datetime, timedelta
from services.fcl_freight_rate.models.cluster_extension_gri_worker import ClusterExtensionGriWorker
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.bramhastra.interactions.list_fcl_freight_rate_statistics import list_fcl_freight_rate_statistics
from services.fcl_freight_rate.helpers.rate_extension_via_bulk_operation import rate_extension_via_bulk_operation
from micro_services.client import common
from fastapi.encoders import jsonable_encoder

MAIN_SHIPPING_LINE_IDS = ['c3649537-0c4b-4614-b313-98540cffcf40']

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

async def update_cluster_extension_by_latest_trends(request):
    today = request.get("start_time")
    start_time, end_time = today - timedelta(hours = 6), today
    
    origin_port_id = request["origin_port_id"]
    destination_port_id = request["destination_port_id"]
    
    min_decrease_percent, max_increase_percent = -5, 10
    min_decrease_amount, max_increase_amount = -100, 500 

    record = (ClusterExtensionGriWorker
            .select(ClusterExtensionGriWorker.min_decrease_percent, ClusterExtensionGriWorker.max_increase_percent, ClusterExtensionGriWorker.min_decrease_amount, ClusterExtensionGriWorker.max_increase_amount)
            .where((ClusterExtensionGriWorker.destination_port_id == destination_port_id) &
            (ClusterExtensionGriWorker.origin_port_id == origin_port_id))).limit(1).first()

    if record:
        min_decrease_percent = record.min_decrease_percent
        max_increase_percent = record.max_increase_percent
        min_decrease_amount = record.min_decrease_amount
        max_increase_amount = record.max_increase_amount


    shipping_line_gri_mapping = {}
    
    query = (FclFreightRate
                .select(FclFreightRate.id,FclFreightRate.container_size, FclFreightRate.shipping_line_id, FclFreightRate.validities) 
                .where(
                    FclFreightRate.updated_at > start_time,
                    FclFreightRate.updated_at < end_time,
                    FclFreightRate.origin_port_id == origin_port_id,
                    FclFreightRate.commodity == request['commodity'],
                    FclFreightRate.container_type == request['container_type'],
                    FclFreightRate.destination_port_id == destination_port_id,
                    ~ FclFreightRate.rate_not_available_entry,
                    ~FclFreightRate.mode.in_(['predicted', 'rate_extension'])     
                ))  
    
    freight_rates = jsonable_encoder(list(query.dicts()))
    for container_size in ["20", "40", "40HC"]:
        rates = [rate for rate in freight_rates if rate["container_size"] == container_size]  
        prices = []
        rate_ids = []
        shipping_line_ids = []
        
        for rate in rates:
            rate_ids.append(rate['id']) 
            shipping_line_ids.append(rate['shipping_line_id'])
            
            price = 0
            for validity in rate['validities']:
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
                    
            prices.append(price / len(rate['validities']))   

        response = await list_fcl_freight_rate_statistics(get_filters(start_time, "average_price", rate_ids, shipping_line_ids), 1, 1, False)
        
        if not response.get('list'):
            continue  
        
        prev_avg_mapping = response['list']

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
            
        for shipping_line_id in average_prices.keys(): 
            cur = average_prices[shipping_line_id]
            prev = prev_avg_mapping[shipping_line_id]
            
            if prev and cur:
                gri_perc = ((cur - prev) / prev) * 100 
                if shipping_line_id in shipping_line_gri_mapping.keys():
                    shipping_line_gri_mapping[shipping_line_id][container_size] = gri_perc
                else:
                    shipping_line_gri_mapping[shipping_line_id] = get_shipping_line_dict()
                    shipping_line_gri_mapping[shipping_line_id][container_size] = gri_perc
                    
    
    shipping_line_avg_mapping = {}

    for key, sub_dict in shipping_line_gri_mapping.items():
        values = []
        for sub_key in sub_dict:
            if sub_dict[sub_key]: 
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
    
    if overall_gri_avg and (min_decrease_percent <= overall_gri_avg <= max_increase_percent):
        request['source'] = 'cluster_extension_worker'
        request["markup"] = overall_gri_avg
        request["shipping_line_id"] = TO_BE_UPDATED_SHIPPING_LINES
        request['source'] = "cluster_extension_worker"
        request["rate_type"] = "market_place"
        request["exclude_service_provider_types"] = ["nvocc"]
        request["min_decrease_amount"] = min_decrease_amount
        request["max_increase_amount"] = max_increase_amount
        
        rate_extension_via_bulk_operation(request)

        request.pop('shipping_line_id')
        request['origin_port_id'] = request.pop('origin_secondary_ports', [])
        request['destination_port_id'] = request.pop('destination_secondary_ports', [])

        rate_extension_via_bulk_operation(request)
        
