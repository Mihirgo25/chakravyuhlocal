from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from micro_services.client import maps, common
from configs.fcl_freight_rate_constants import (
    FCL_FREIGHT_FALLBACK_FAKE_SCHEDULES,
    DEFAULT_SCHEDULE_TYPES,
)
import json

REQUIRED_SCHEDULE_KEYS = [ "departure","arrival","number_of_stops","transit_time","legs","si_cutoff","vgm_cutoff","schedule_type","reliability_score","terminal_cutoff", "source" ,"id"]
INDIA_COUNTRY_CURRENCY = "INR"

def create_sailing_schedules_hash(executors,sailing_schedules,sailing_schedules_hash):
    for executor in executors:
        results = executor.result()
        sailing_schedules.extend(results)
        
    for sailing_schedule in sailing_schedules:
        key = ":".join(
            [
                sailing_schedule["origin_port_id"],
                sailing_schedule["destination_port_id"],
                sailing_schedule["shipping_line_id"],
            ]
        )
        schedule_data = { k: sailing_schedule.get(k, None) for k in REQUIRED_SCHEDULE_KEYS }
        
        if key in sailing_schedules_hash:
            sailing_schedules_hash[key].append(schedule_data)
        else:
            sailing_schedules_hash[key] = [schedule_data]
        
    return sailing_schedules_hash  


def get_relavant_schedules(data,origin_port,destination_port,origin_port_id,destination_port_id,sailing_schedules_hash):
    key = []
    key.append(data["origin_main_port_id"] if origin_port["is_icd"] else origin_port_id)
    key.append(data["destination_main_port_id"] if destination_port["is_icd"] else destination_port_id)
    key.append(data["shipping_line_id"])
    key = ":".join(key)

    data_schedules = sailing_schedules_hash.get(key, []) 
    
    return data_schedules


def update_grouping(data,currency,locals_price,sailing_schedules_required,detention_free_limit,grouping,spot_search_object):
    
    for freight in data["freights"]:
        freight_price = sum(
            common.get_money_exchange_for_fcl(
                data={
                "from_currency": line_item["currency"],
                "to_currency": currency,
                "price": line_item["total_price"],
                'organization_id':spot_search_object["importer_exporter_id"]

                }
            ).get("price")
            for line_item in freight["line_items"]
        )
        total_price = float(freight_price) + float(locals_price)

        if sailing_schedules_required and data["source"] != "cogo_assured_rate":
            key_elements = [
                data["shipping_line_id"],
                str(freight["departure"] or ""),
                str(freight["arrival"] or "") ,
                str(freight["number_of_stops"] or "") ,
                data["origin_main_port_id"] or "",
                data["destination_main_port_id"] or "",
                str(detention_free_limit) or "",
                data["source"],
            ]
        else:
            key_elements = [
                data["shipping_line_id"],
                str(freight["validity_start"] or "") ,
                str(freight["validity_end"] or "") ,
                str(freight["number_of_stops"] or "") ,
                data["origin_main_port_id"] or "",
                data["destination_main_port_id"] or "",
                str(detention_free_limit) or "",
                data["source"],
            ]

        key = ":".join(key_elements)
        
        if (key not in grouping) or (grouping[key]["total_price"] > total_price) or (grouping[key]["total_price"] == total_price and grouping[key]["freight_price"] > freight_price):
            data["freights"] = [freight]
            grouping[key] = {
                "total_price": total_price,
                "freight_price": freight_price,
                "data": {**data,'freights' : [freight]}  
            }
            
    return grouping            

def get_freight_schedules(freight, data_schedules, selected_schedule_ids,origin_port_id, destination_port_id):
    schedules = None
    schedule_found = False
    
    if freight.get('schedule_id'):
        schedules = [schedule for schedule in data_schedules if freight.get('schedule_id') == schedule.get('id')]
        if schedules:
            schedule_found = True
            selected_schedule_ids.add(schedules[0]['id'])    
    
    if not schedules: 
        schedules = [
            schedule
            for schedule in data_schedules
            if datetime.strptime(freight["validity_start"], "%Y-%m-%d").date() <= datetime.strptime(schedule["departure"], "%Y-%m-%d").date()
            and datetime.strptime(freight["validity_end"], "%Y-%m-%d").date() >= datetime.strptime(schedule["departure"], "%Y-%m-%d").date()
            and freight["schedule_type"] == schedule.get("schedule_type")
        ]

    if not schedules:
        transit_times = [schedule["transit_time"] for schedule in data_schedules]
        avg_transit_time = sum(transit_times) / len(transit_times) if transit_times else None

        if avg_transit_time is None:
            data = {
                        "origin_port_id": origin_port_id,
                        "destination_port_id": destination_port_id,
                    }
            predicted_transit_time = maps.get_predicted_transit_time(data)
        
        fallback_schedules = FCL_FREIGHT_FALLBACK_FAKE_SCHEDULES
        
        for fake_schedule in fallback_schedules:
            fake_schedule["transit_time"] = (
                avg_transit_time
                or predicted_transit_time
                or fake_schedule["transit_time"]
            )

        for fake_schedule in fallback_schedules:
            departure = (datetime.now() + timedelta(days=fake_schedule["departure_offset_days"])).date()
            cur_validity_end = datetime.strptime(freight["validity_end"], "%Y-%m-%d").date()
            cur_validity_start = datetime.strptime(freight["validity_start"], "%Y-%m-%d").date()

            if departure > cur_validity_end:
                departure = cur_validity_end
            if departure < cur_validity_start:
                departure = cur_validity_start

            schedule = {
                "departure": departure,
                "transit_time": fake_schedule["transit_time"],
                "number_of_stops": fake_schedule["number_of_stops"],
                "schedule_type": fake_schedule["schedule_type"],
                "source": "fake",
            }
            schedule["arrival"] = schedule["departure"] + timedelta(days=schedule["transit_time"])
            schedules.append(schedule)   
              
    return schedules, schedule_found       
            
            
def get_freights(data,sailing_schedules_required,data_schedules,origin_port_id,destination_port_id):
    
        freights = []
        
        if sailing_schedules_required and data["source"] != "cogo_assured_rate":
            selected_schedule_ids = set()
            
            for freight in data["freights"]:
                if freight["schedule_type"] in ["transhipment", "transshipment"]:
                    freight["schedule_type"] = "transshipment"
                    
                schedules, schedule_found = get_freight_schedules(freight, data_schedules, selected_schedule_ids,origin_port_id, destination_port_id)
            
                for sailing_schedule in schedules:
                    freight_line_items = list(freight["line_items"])
                    
                    for item in freight_line_items:
                        item['price'] = float(item['price'])
                    if not schedule_found and sailing_schedule.get('id') in selected_schedule_ids:
                        continue
                    
                    freights.append(
                        {
                            "line_items": json.loads(json.dumps(freight_line_items)),
                            "departure": sailing_schedule.get("departure"),
                            "arrival": sailing_schedule.get("arrival"),
                            "number_of_stops": sailing_schedule.get("number_of_stops"),
                            "transit_time": sailing_schedule.get("transit_time"),
                            "legs": sailing_schedule.get("legs"),
                            "si_cutoff": sailing_schedule.get("si_cutoff"),
                            "vgm_cutoff": sailing_schedule.get("vgm_cutoff"),
                            "reliability_score": sailing_schedule.get("reliability_score"),
                            "schedule_type": sailing_schedule.get("schedule_type"),
                            "terminal_cutoff": sailing_schedule.get("terminal_cutoff"),
                            "schedule_source": sailing_schedule.get("source"),
                            "validity_start": freight.get("validity_start"),
                            "validity_end": freight.get("validity_end"),
                            "validity_id": freight.get("validity_id"),
                            "likes_count": freight.get("likes_count"),
                            "dislikes_count": freight.get("dislikes_count"),
                            "service_id": freight.get("service_id"),
                            "payment_term": freight.get("payment_term"),
                        }
                    )

        if not sailing_schedules_required or data["source"] == "cogo_assured_rate":
            for freight_object in data["freights"]:
                freight_line_items = list(freight_object["line_items"])
                for item in freight_line_items:
                    item['price'] = float(item['price'])
                freights.append(
                    {
                        "line_items": json.loads(json.dumps(freight_line_items)),
                        "departure": None,
                        "arrival": None,
                        "number_of_stops": None,
                        "transit_time": None,
                        "validity_start": freight_object.get("validity_start"),
                        "validity_end": freight_object.get("validity_end"),
                        "schedule_type": freight_object.get("schedule_type", DEFAULT_SCHEDULE_TYPES),
                        "validity_id": freight_object.get("validity_id"),
                        "likes_count": freight_object.get("likes_count"),
                        "dislikes_count": freight_object.get("dislikes_count"),
                        "service_id": freight_object.get("service_id"),
                    }
                )
                
        return freights        


def get_sailing_schedules_data(port_pair, shipping_line,validity_start):
    origin_port_id = port_pair.split("_")[0]
    destination_port_id = port_pair.split("_")[1]
    
    data = {
        "origin_port_id": origin_port_id,
        "destination_port_id": destination_port_id,
        "filters": {
            'shipping_line_id': list(set(shipping_line)),
            "departure_start": validity_start
        },
        "page_limit": 1000,
        "sort_by": "departure",
        "sort_type": "asc",
        "request_source":"spot_search"
    }

    response = maps.get_sailing_schedules(data)
    schedules = response.get('list',[])
    
    for schedule in schedules:
        schedule["origin_port_id"] = origin_port_id
        schedule["destination_port_id"] = destination_port_id
    
    return schedules
  
             
def get_fcl_freight_rate_cards_schedules(filters):
    origin_port_id=filters.get('origin_port_id')
    origin_trade_id=filters.get('origin_trade_id')
    origin_country_id=filters.get('origin_country_id')
    destination_port_id=filters.get('destination_port_id')
    destination_trade_id=filters.get('destination_trade_id')
    destination_country_id=filters.get('destination_country_id')
    port_pairs=filters.get('port_pairs')
    sailing_schedules_required=filters.get('sailing_schedules_required')
    validity_start=filters.get('validity_start')
    list_data=filters.get('list_data')
    spot_search_object=filters.get('spot_search_object')
    origin_port=filters.get('origin_port')
    destination_port=filters.get('destination_port')
    
    fake_schedules = []
    sailing_schedules_hash = {}

    if sailing_schedules_required:
        sailing_schedules = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            executors = [
                executor.submit(get_sailing_schedules_data, port_pair, shipping_line,validity_start)
                for port_pair, shipping_line in port_pairs.items()
            ]
          
        sailing_schedules_hash=create_sailing_schedules_hash(executors,sailing_schedules,sailing_schedules_hash)  

        rates = []
        data = {
                "origin_port_id": origin_port_id,
                "origin_trade_id": origin_trade_id,
                "origin_country_id": origin_country_id,
                "destination_port_id": destination_port_id,
                "destination_trade_id": destination_trade_id,
                "destination_country_id": destination_country_id
            }
        
        response = maps.get_fake_sailing_schedules(data)
        fake_schedules = response['list']

    grouping = {}

    for data in list_data:
        data_schedules = get_relavant_schedules(
            data,
            origin_port,
            destination_port,
            origin_port_id,
            destination_port_id,
            sailing_schedules_hash
        )
        if not data_schedules:
            data_schedules = fake_schedules

        data_schedules = list(data_schedules)
        freights = get_freights(data,sailing_schedules_required,data_schedules,origin_port_id,destination_port_id)

        if not freights:
            continue

        data["freights"] = freights

        currency = INDIA_COUNTRY_CURRENCY
        locals_price = sum(
            common.get_money_exchange_for_fcl(
                data={
                    "from_currency": line_item["currency"],
                    "to_currency": currency,
                    "price": line_item["total_price"],
                    'organization_id':spot_search_object["importer_exporter_id"]
                }
            ).get("price")
            for line_item in (data.get("origin_local", {}).get("line_items", []) + data.get("destination_local", {}).get("line_items", []))
        )

        detention_free_limit = int(data["destination_detention"].get("free_limit", 0))
        grouping = update_grouping(
            data,
            currency,
            locals_price,
            sailing_schedules_required,
            detention_free_limit,
            grouping,
            spot_search_object
        )

    rates = [v["data"] for v in grouping.values()]

    return {'list' : rates}
