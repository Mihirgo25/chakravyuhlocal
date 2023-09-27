from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from micro_services.client import common
from configs.fcl_freight_rate_constants import (
    FCL_FREIGHT_FALLBACK_FAKE_SCHEDULES,
    DEFAULT_SCHEDULE_TYPES,
)
import json


def get_fcl_freight_rate_cards_schedules(filters):
    
    origin_port_id=filters.get('origin_port_id')
    origin_trade_id=filters.get('origin_trade_id')
    origin_continent_id=filters.get('origin_continent_id')
    destination_port_id=filters.get('destination_port_id')
    destination_trade_id=filters.get('destination_trade_id')
    destination_continent_id=filters.get('destination_continent_id')
    port_pairs=filters.get('port_pairs')
    sailing_schedules_required=filters.get('sailing_schedules_required')
    validity_start=filters.get('validity_start')
    list_data=filters.get('list')
    spot_search_object=filters.get('spot_search_object')
    origin_port=filters.get('origin_port')
    destination_port=filters.get('destination_port')
    
    
    fake_schedules = []
    sailing_schedules_hash = {}
    

    if sailing_schedules_required:

        def get_sailing_schedules_new(port_pair, shipping_line):
            origin_port_id = port_pair.split("_")[0]
            destination_port_id = port_pair.split("_")[1]
            
            data = {
                "origin_port_id": origin_port_id,
                "destination_port_id": destination_port_id,
                "filters": {
                    # 'shipping_line_id': shipping_line_ids,
                    "departure_start": validity_start
                },
                "page_limit": 1000,
                "sort_by": "departure",
                "sort_type": "asc",
                "request_source": "spot_search",
            }
            schedules = common.get_sailing_schedules(data)

            return [
                {
                    "origin_port_id": origin_port_id,
                    "destination_port_id": destination_port_id,
                    **t,
                }
                for t in schedules["list"]
            ]

        sailing_schedules = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            executors = [
                executor.submit(get_sailing_schedules_new, port_pair, shipping_line)
                for port_pair, shipping_line in port_pairs.items()
            ]
          

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

            schedule_data = {
                k: sailing_schedule.get(k, None)
                for k in [ "departure","arrival","number_of_stops","transit_time","legs","si_cutoff","vgm_cutoff","schedule_type",
                    "reliability_score","terminal_cutoff", "source" ]
                }

            sailing_schedules_hash.setdefault(key, []).append(schedule_data)
    
        rates = []
        data = {
                "origin_port_id": origin_port_id,
                "origin_trade_id": origin_trade_id,
                "origin_continent_id": origin_continent_id,
                "destination_port_id": destination_port_id,
                "destination_trade_id": destination_trade_id,
                "destination_continent_id": destination_continent_id,
            }

        fake_schedules = common.get_fake_sailing_schedules(data)

    grouping = {}

    for data in list_data:
        key = []
        key.append(
            data["origin_main_port_id"] if origin_port["is_icd"] else origin_port_id
        )
        key.append(
            data["destination_main_port_id"]
            if destination_port["is_icd"]
            else destination_port_id
        )
        key.append(data["shipping_line_id"])
        key = ":".join(key)

        data_schedules = sailing_schedules_hash.get(key, [])
        
        if not data_schedules:
            data_schedules = fake_schedules

        data_schedules = list(data_schedules)
 
        freights = []

        if sailing_schedules_required and data["source"] != "cogo_assured_rate":
            for freight in data["freights"]:
                if freight["schedule_type"] in ["transhipment", "transshipment"]:
                    freight["schedule_type"] = "transshipment"

                schedules = [
                    schedule
                    for schedule in data_schedules
                    if freight["validity_start"] <= schedule["departure"]
                    and freight["validity_end"] >= schedule["departure"]
                    and freight["schedule_type"] == schedule.get("schedule_type")
                ]
          
                if not schedules:
                    transit_times = [
                        schedule["transit_time"] for schedule in data_schedules
                    ]
                    avg_transit_time = (
                        sum(transit_times) / len(transit_times)
                        if transit_times
                        else None
                    )

                    if avg_transit_time is None:
                        data = {
                                    "origin_port_id": origin_port_id,
                                    "destination_port_id": destination_port_id,
                                }
                        predicted_transit_time = common.get_predicted_transit_time(data)

                    fallback_schedules = FCL_FREIGHT_FALLBACK_FAKE_SCHEDULES
                   
                    for fake_schedule in fallback_schedules:
                        fake_schedule["transit_time"] = (
                            avg_transit_time
                            or predicted_transit_time
                            or fake_schedule["transit_time"]
                        )

                    for fake_schedule in fallback_schedules:
                        departure = (
                            datetime.now()
                            + timedelta(days=fake_schedule["departure_offset_days"])
                        ).date()
                        cur_validity_end = datetime.strptime(
                            freight["validity_end"], "%Y-%m-%d"
                        ).date()
                        cur_validity_start = datetime.strptime(
                            freight["validity_start"], "%Y-%m-%d"
                        ).date()

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
            
                for sailing_schedule in schedules:
                    freight_line_items = list(freight["line_items"])

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

        if not freights:
            continue

        data["freights"] = freights

        currency = "INR"
        locals_price = sum(
            common.get_money_exchange_for_fcl(
                data={
                    "from_currency": line_item["currency"],
                    "to_currency": currency,
                    "price": line_item["total_price"],
                    'organization_id':spot_search_object["importer_exporter_id"],
                    'source':"default"
                }
            ).get("price", 0)
            for line_item in (
                data.get("origin_local", {}).get("line_items", [])
                + data.get("destination_local", {}).get("line_items", [])
            )
        )

        detention_free_limit = int(data["destination_detention"].get("free_limit", 0))

        for freight in data["freights"]:
            freight_price = sum(
                common.get_money_exchange_for_fcl(
                    data={
                    "from_currency": line_item["currency"],
                    "to_currency": currency,
                    "price": line_item["total_price"],
                    'organization_id':spot_search_object["importer_exporter_id"],
                    'source':"default"
                    }
                ).get("price", 0)
                for line_item in freight["line_items"]
            )

            total_price = freight_price + locals_price

            if sailing_schedules_required and data["source"] != "cogo_assured_rate":
                key_elements = [
                    data["shipping_line_id"],
                    str(freight["departure"]) if freight["departure"] is not None else "",
                    str(freight["arrival"]) if freight["arrival"] is not None else "",
                    str(freight["number_of_stops"]) if freight["number_of_stops"] is not None else "",
                    data["origin_main_port_id"] if data["origin_main_port_id"] is not None else "",
                    data["destination_main_port_id"] if data["destination_main_port_id"] is not None else "",
                    str(detention_free_limit) if detention_free_limit is not None else "",
                    data["source"],
                ]

                key = ":".join(key_elements)

            else:
                key_elements = [
                    data["shipping_line_id"],
                    str(freight["validity_start"]) if freight["validity_start"] is not None else "",
                    str(freight["validity_end"]) if freight["validity_end"] is not None else "",
                    str(freight["number_of_stops"]) if freight["number_of_stops"] is not None  else "",
                    data["origin_main_port_id"] if data["origin_main_port_id"] is not None else "",
                    data["destination_main_port_id"] if data["destination_main_port_id"] is not None else "",
                    str(detention_free_limit) if detention_free_limit is not None else "",
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
            
    
    rates = [v["data"] for v in grouping.values()]
    
    return rates
