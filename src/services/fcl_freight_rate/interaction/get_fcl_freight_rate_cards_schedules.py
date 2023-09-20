from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from micro_services.client import common
from configs.fcl_freight_rate_constants import (
    FCL_FREIGHT_FALLBACK_FAKE_SCHEDULES,
    DEFAULT_SCHEDULE_TYPES,
)


def get_sailing_schedules_data(
    origin_port_id,
    destination_port_id,
    shipping_line_ids,
    validity_start,
    page_limit,
    sort_by,
    sort_type,
    request_source,
    validity_end,
):
    schedules = common.get_sailing_schedules(
        origin_port_id,
        destination_port_id,
        shipping_line_ids,
        validity_start,
        page_limit,
        sort_by,
        sort_type,
        request_source,
        validity_end=validity_end,  
    )
    return schedules



def get_fake_schedules_data(
    origin_port_id,
    origin_trade_id,
    origin_continent_id,
    destination_port_id,
    destination_trade_id,
    destination_continent_id,
):
    fake_schedules = common.get_fake_sailing_schedules(
        origin_port_id,
        origin_trade_id,
        origin_continent_id,
        destination_port_id,
        destination_trade_id,
        destination_continent_id,
    )
    return fake_schedules


def get_predicted_transit_time_data(origin_port_id, destination_port_id):
    predicted_transit_time = common.get_predicted_transit_time(
        origin_port_id, destination_port_id
    )
    return predicted_transit_time


def get_money_exchange_data(price, from_currency, to_currency, organization_id, source):
    exchange_rate = common.get_money_exchange(
        price, from_currency, to_currency, organization_id, source
    )
    return exchange_rate["price"]


def get_fcl_freight_rate_cards_schedules(
    origin_port_id,
    origin_trade_id,
    origin_continent_id,
    destination_port_id,
    destination_trade_id,
    destination_continent_id,
    port_pairs,
    sailing_schedules_required,
    validity_start,
    list,
    spot_search_object,
):
    sailing_schedules_hash = {}
    fake_schedules = []

    if sailing_schedules_required:

        def get_sailing_schedules(port_pair):
            origin_port_id = port_pair.split("_")[0]
            destination_port_id = port_pair.split("_")[1]

            schedules = get_sailing_schedules_data(
                origin_port_id=origin_port_id,
                destination_port_id=destination_port_id,
                shipping_line_ids=list(set(port_pair.last)),
                validity_start=validity_start,
                page_limit=1000,
                sort_by="departure",
                sort_type="asc",
                request_source="spot_search",  
                validity_end=freight_object['validity_end'],
            )

            return [
                {
                    "origin_port_id": origin_port_id,
                    "destination_port_id": destination_port_id,
                    **t,
                }
                for t in schedules
            ]

        with ThreadPoolExecutor() as executor:
            executors = [
                executor.submit(get_sailing_schedules, port_pair)
                for port_pair in port_pairs
            ]

        sailing_schedules = [
            result for executor in executors for result in executor.result()
        ]

        for sailing_schedule in sailing_schedules:
            key = ":".join(
                [
                    sailing_schedule["origin_port_id"],
                    sailing_schedule["destination_port_id"],
                    sailing_schedule["shipping_line_id"],
                ]
            )
            sailing_schedules_hash.setdefault(key, []).append(
                {
                    k: sailing_schedule[k]
                    for k in [
                        "departure",
                        "arrival",
                        "number_of_stops",
                        "transit_time",
                        "legs",
                        "si_cutoff",
                        "vgm_cutoff",
                        "schedule_type",
                        "reliability_score",
                        "terminal_cutoff",
                        "source",
                    ]
                }
            )

        rates = []

        fake_schedules = get_fake_schedules_data(
            origin_port_id=origin_port_id,
            origin_trade_id=origin_trade_id,
            origin_continent_id=origin_continent_id,
            destination_port_id=destination_port_id,
            destination_trade_id=destination_trade_id,
            destination_continent_id=destination_continent_id,
        )

    grouping = {}

    for data in list:
        key = []
        key.append(
            data["origin_main_port_id"]
            if data["origin_port"]["is_icd"]
            else origin_port_id
        )
        key.append(
            data["destination_main_port_id"]
            if data["destination_port"]["is_icd"]
            else destination_port_id
        )
        key.append(data["shipping_line_id"])
        key = ":".join(key)

        data_schedules = sailing_schedules_hash.get(key, [])

        if not data_schedules:
            data_schedules = fake_schedules

        data_schedules = list(data_schedules)

        for sailing_schedule in data_schedules:
            sailing_schedule["departure"] = sailing_schedule["departure"].date()
            sailing_schedule["arrival"] = sailing_schedule["arrival"].date()

        freights = []

        if sailing_schedules_required and data["source"] != "cogo_assured_rate":
            for freight in data["freights"]:
                if freight["schedule_type"] in ["transhipment", "transshipment"]:
                    freight["schedule_type"] = "transshipment"

                schedules = [
                    schedule
                    for schedule in data_schedules
                    if freight["validity_start"]
                    <= schedule["departure"]
                    <= freight["validity_end"]
                    and freight["schedule_type"] == schedule["schedule_type"]
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
                        predicted_transit_time = get_predicted_transit_time_data(
                            origin_port_id=data["origin_port_id"],
                            destination_port_id=data["destination_port_id"],
                        )

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
                        if departure > freight["validity_end"].date():
                            departure = freight["validity_end"].date()
                        if departure < freight["validity_start"].date():
                            departure = freight["validity_start"].date()

                        schedule = {
                            "departure": departure,
                            "transit_time": fake_schedule["transit_time"],
                            "number_of_stops": fake_schedule["number_of_stops"],
                            "schedule_type": fake_schedule["schedule_type"],
                            "source": "fake",
                        }
                        schedule["arrival"] = (
                            schedule["departure"]
                            + timedelta(days=schedule["transit_time"])
                        ).date()

                        schedules.append(schedule)

                for sailing_schedule in schedules:
                    freight_line_items = list(freight["line_items"])

                    freights.append(
                        {
                            "line_items": list(freight_line_items),
                            "departure": sailing_schedule["departure"],
                            "arrival": sailing_schedule["arrival"],
                            "number_of_stops": sailing_schedule["number_of_stops"],
                            "transit_time": sailing_schedule["transit_time"],
                            "legs": sailing_schedule["legs"],
                            "si_cutoff": sailing_schedule["si_cutoff"],
                            "vgm_cutoff": sailing_schedule["vgm_cutoff"],
                            "reliability_score": sailing_schedule["reliability_score"],
                            "schedule_type": sailing_schedule["schedule_type"],
                            "terminal_cutoff": sailing_schedule["terminal_cutoff"],
                            "schedule_source": sailing_schedule["source"],
                            "validity_start": freight["validity_start"],
                            "validity_end": freight["validity_end"],
                            "validity_id": freight["validity_id"],
                            "likes_count": freight["likes_count"],
                            "dislikes_count": freight["dislikes_count"],
                            "service_id": freight["service_id"],
                            "payment_term": freight["payment_term"],
                        }
                    )

        if not sailing_schedules_required or data["source"] == "cogo_assured_rate":
            for freight_object in data["freights"]:
                freight_line_items = list(freight_object["line_items"])

                freights.append(
                    {
                        "line_items": list(freight_line_items),
                        "departure": None,
                        "arrival": None,
                        "number_of_stops": None,
                        "transit_time": None,
                        "validity_start": freight_object["validity_start"],
                        "validity_end": freight_object["validity_end"],
                        "schedule_type": freight_object.get(
                            "schedule_type", DEFAULT_SCHEDULE_TYPES
                        ),
                        "validity_id": freight_object["validity_id"],
                        "likes_count": freight_object["likes_count"],
                        "dislikes_count": freight_object["dislikes_count"],
                        "service_id": freight_object["service_id"],
                    }
                )

        if freights:
            data["freights"] = freights

            currency = "INR"

            locals_price = sum(
                get_money_exchange_data(
                    price=line_item["total_price"],
                    from_currency=line_item["currency"],
                    to_currency=currency,
                    organization_id=spot_search_object.importer_exporter_id,
                    source="default",
                )
                for line_item in (
                    data["origin_local"].get("line_items", [])
                    + data["destination_local"].get("line_items", [])
                )
            )

            detention_free_limit = int(
                data["destination_detention"].get("free_limit", 0)
            )

            for freight in data["freights"]:
                freight_price = sum(
                    get_money_exchange_data(
                        price=line_item["total_price"],
                        from_currency=line_item["currency"],
                        to_currency=currency,
                        organization_id=spot_search_object.importer_exporter_id,
                        source="default",
                    )
                    for line_item in freight["line_items"]
                )

                total_price = freight_price + locals_price

                if sailing_schedules_required and data["source"] != "cogo_assured_rate":
                    key = ":".join(
                        [
                            data["shipping_line_id"],
                            str(freight["departure"]),
                            str(freight["arrival"]),
                            str(freight["number_of_stops"]),
                            data["origin_main_port_id"],
                            data["destination_main_port_id"],
                            str(detention_free_limit),
                            data["source"],
                        ]
                    )
                else:
                    key = ":".join(
                        [
                            data["shipping_line_id"],
                            str(freight["validity_start"].date()),
                            str(freight["validity_end"].date()),
                            data["origin_main_port_id"],
                            data["destination_main_port_id"],
                            str(detention_free_limit),
                            data["source"],
                        ]
                    )

                if key not in grouping or (
                    grouping[key]["total_price"] > total_price
                    or (
                        grouping[key]["total_price"] == total_price
                        and grouping[key]["freight_price"] > freight_price
                    )
                ):
                    grouping[key] = {
                        "total_price": total_price,
                        "freight_price": freight_price,
                        "data": {k: data[k] for k in data.keys() if k != "freights"},
                    }

    rates = [v["data"] for v in grouping.values()]

    return rates
