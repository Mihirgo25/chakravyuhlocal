from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from micro_services.client import maps, common, schedule_client
from configs.fcl_freight_rate_constants import (
    FCL_FREIGHT_FALLBACK_FAKE_SCHEDULES,
    DEFAULT_SCHEDULE_TYPES,
)
import json
import sentry_sdk
import traceback
from services.fcl_freight_rate.interaction.get_fcl_freight_rate_cards import (
    get_fcl_freight_rate_cards,
)
from libs.common_validations import handle_empty_ids
from libs.convert_date_format import convert_date_format


REQUIRED_SCHEDULE_KEYS = [
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
    "id",
]
INDIA_COUNTRY_CURRENCY = "INR"


def generate_sailing_schedules_hash(sailing_schedules):
    """
    Create a hash of sailing schedules and update the existing sailing schedules.
    Returns:
        dict: Updated sailing schedules hash.
    """
    sailing_schedules_hash = {}

    for sailing_schedule in sailing_schedules:
        key = ":".join(
            [
                sailing_schedule["origin_port_id"],
                sailing_schedule["destination_port_id"],
                sailing_schedule["shipping_line_id"],
            ]
        )
        schedule_data = {
            k: sailing_schedule.get(k, None) for k in REQUIRED_SCHEDULE_KEYS
        }

        if key in sailing_schedules_hash:
            sailing_schedules_hash[key].append(schedule_data)
        else:
            sailing_schedules_hash[key] = [schedule_data]

    return sailing_schedules_hash


def get_relevant_schedules(
    data,
    origin_port,
    destination_port,
    origin_port_id,
    destination_port_id,
    sailing_schedules_hash,
):
    """Retrieve data_schedules based on provided data and the sailing schedules hash.
    Returns:
        list: List of relevant schedules for the given data.
    """
    key = []
    key.append(data["origin_main_port_id"] if origin_port["is_icd"] else origin_port_id)
    key.append(
        data["destination_main_port_id"]
        if destination_port["is_icd"]
        else destination_port_id
    )
    key.append(data["shipping_line_id"])
    key = ":".join(key)

    data_schedules = sailing_schedules_hash.get(key, [])

    return data_schedules


def update_grouping(
    data,
    currency,
    locals_price,
    sailing_schedules_required,
    detention_free_limit,
    grouping,
    importer_exporter_id,
):
    """
    Update a grouping of freight data based on criteria.
    Returns:
        dict: Updated grouping of data.
    Process:
    1. For each freight in the provided data:
    2. Calculate the total price by summing up prices for line items after currency conversion.
    3. Compute the total price for the freight.
    4. Determine the key elements based on whether sailing schedules are required.
    5. Create a key by joining key elements.
    6. Check if the key is not in the existing grouping or if the new data has a lower total price.
    7. If so, update the grouping with the new freight data.
    8. Return the updated grouping.
    """

    for freight in data["freights"]:
        freight_price = sum(
            common.get_money_exchange_for_fcl(
                data={
                    "from_currency": line_item["currency"],
                    "to_currency": currency,
                    "price": line_item["total_price"],
                    "organization_id": importer_exporter_id,
                }
            ).get("price")
            for line_item in freight["line_items"]
        )
        total_price = float(freight_price) + float(locals_price)

        if sailing_schedules_required and data["source"] != "cogo_assured_rate":
            key_elements = [
                data.get("shipping_line_id"),
                str(freight.get("departure") or ""),
                str(freight.get("arrival") or ""),
                str(freight.get("number_of_stops") or ""),
                data.get("origin_main_port_id") or "",
                data.get("destination_main_port_id") or "",
                str(detention_free_limit) or "",
                data.get("source"),
            ]
        else:
            key_elements = [
                data.get("shipping_line_id"),
                str(freight.get("validity_start") or ""),
                str(freight.get("validity_end") or ""),
                str(freight.get("number_of_stops") or ""),
                data.get("origin_main_port_id") or "",
                data.get("destination_main_port_id") or "",
                str(detention_free_limit) or "",
                data.get("source"),
            ]

        key = ":".join(key_elements)

        if (
            (key not in grouping)
            or (grouping[key]["total_price"] > total_price)
            or (
                grouping[key]["total_price"] == total_price
                and grouping[key]["freight_price"] > freight_price
            )
        ):
            data["freights"] = [freight]
            grouping[key] = {
                "total_price": total_price,
                "freight_price": freight_price,
                "data": {**data, "freights": [freight]},
            }

    return grouping


def get_transit_time(data_schedules):
    transit_time = [
        schedule["transit_time"]
        or int(
            (
                convert_date_format(schedule["arrival"], dayfirst=False)
                - convert_date_format(schedule["departure"], dayfirst=False)
            ).days
        )
        for schedule in data_schedules
    ]

    return transit_time


def get_freight_schedules(
    freight, data_schedules, selected_schedule_ids, predicted_transit_time
):
    """
    Retrieve freight_schedules for the given freight data.
    Returns:
        list: List of relevant schedules for the freight.
        bool: Whether a matching schedule was found.
    Process:
    1. Check if the freight has a specific schedule ID and try to match it with data_schedules.
    2. If a matching schedule is found, mark it as selected.
    3. If no specific schedule is found, search for schedules based on validity dates and schedule type.
    4. If still no schedules are found, calculate an average transit time and use fake schedules as a fallback.
    5. Return the list of schedules and whether a matching schedule was found.
    """

    schedules = []
    should_create_fake_schedules = True

    if freight.get("schedule_id"):
        schedules = [
            schedule
            for schedule in data_schedules
            if freight.get("schedule_id") == schedule.get("id")
        ]
        if schedules:
            return schedules

    for schedule in data_schedules:
        if (
            freight["validity_start"]
            <= datetime.strptime(schedule["departure"], "%Y-%m-%d").date()
            and freight["validity_end"]
            >= datetime.strptime(schedule["departure"], "%Y-%m-%d").date()
            and freight.get("schedule_type") == schedule.get("schedule_type")
        ):
            if schedule.get("id") in selected_schedule_ids:
                should_create_fake_schedules = False
                continue
            schedules.append(schedule)

    if not schedules and should_create_fake_schedules:
        transit_times = get_transit_time(data_schedules)
        avg_transit_time = (
            sum(transit_times) / len(transit_times) if transit_times else None
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
                datetime.now() + timedelta(days=fake_schedule["departure_offset_days"])
            ).date()
            cur_validity_end = freight["validity_end"]
            cur_validity_start = freight["validity_start"]

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
            schedule["arrival"] = schedule["departure"] + timedelta(
                days=schedule["transit_time"]
            )
            schedules.append(schedule)

    return schedules


def get_freights(
    data,
    sailing_schedules_required,
    data_schedules,
    predicted_transit_time,
    selected_schedule_ids,
):
    """
    Structure freights based on provided data.
    Returns:
        list: List of structured freights based on the provided data.
    Process:
    1. If sailing schedules are required and the data source is not "cogo_assured_rate," find relevant schedules.
    2. Structure the freights based on the matching schedules.
    3. If no matching schedules are found, use fake schedules as a fallback.
    4. If sailing schedules are not required or the source is "cogo_assured_rate," structure freights without schedules.
    5. Return the list of structured freights.
    """
    freights = []

    if sailing_schedules_required and data["source"] != "cogo_assured_rate":
        for freight in data["freights"]:
            if freight.get("schedule_type") in ["transhipment", "transshipment"]:
                freight["schedule_type"] = "transshipment"

            schedules = get_freight_schedules(
                freight, data_schedules, selected_schedule_ids, predicted_transit_time
            )
            for sailing_schedule in schedules:
                freight_line_items = list(freight["line_items"])

                for item in freight_line_items:
                    item["price"] = float(item["price"])

                freights.append(
                    {
                        "line_items": json.loads(json.dumps(freight_line_items)),
                        "departure": sailing_schedule.get("departure"),
                        "arrival": sailing_schedule.get("arrival"),
                        "number_of_stops": sailing_schedule.get("number_of_stops"),
                        "transit_time": sailing_schedule.get("transit_time"),
                        "legs": [],
                        "schedule_id": sailing_schedule.get("id"),
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
                item["price"] = float(item["price"])
            freights.append(
                {
                    "line_items": json.loads(json.dumps(freight_line_items)),
                    "departure": None,
                    "arrival": None,
                    "number_of_stops": None,
                    "transit_time": None,
                    "validity_start": freight_object.get("validity_start"),
                    "validity_end": freight_object.get("validity_end"),
                    "schedule_type": freight_object.get(
                        "schedule_type", DEFAULT_SCHEDULE_TYPES
                    ),
                    "validity_id": freight_object.get("validity_id"),
                    "likes_count": freight_object.get("likes_count"),
                    "dislikes_count": freight_object.get("dislikes_count"),
                    "service_id": freight_object.get("service_id"),
                }
            )

    return freights


def get_sailing_schedules_data(port_pair, shipping_line, validity_start):
    """Retrieve sailing schedule data for a specific port pair, shipping line, and validity start date.
    Returns:
        list: A list of sailing schedules that match the specified criteria.
    Process:
    1. Split the port_pair string to obtain the origin_port_id and destination_port_id.
    2. Construct a data dictionary with filters, specifying shipping_line_id and departure_start.
    3. Send a request to obtain sailing schedule data using the constructed data.
    4. Extract the list of schedules from the response.
    5. Add the origin_port_id and destination_port_id to each schedule in the list.
    6. Return the list of sailing schedules that match the criteria.

    """
    origin_port_id = port_pair.split("_")[0]
    destination_port_id = port_pair.split("_")[1]

    data = {
        "origin_port_id": origin_port_id,
        "destination_port_id": destination_port_id,
        "filters": {
            "shipping_line_id": list(set(shipping_line)),
            "departure_start": str(validity_start),
        },
        "page_limit": 1000,
        "sort_by": "departure",
        "sort_type": "asc",
        "request_source": "spot_search",
    }

    response = schedule_client.get_sailing_schedules(data)
    schedules = response.get("list", [])

    for schedule in schedules:
        schedule["origin_port_id"] = origin_port_id
        schedule["destination_port_id"] = destination_port_id

    return schedules


def get_location_data(origin_port_id, destination_port_id):
    locations_list = maps.list_locations(
        {
            "filters": {"id": [origin_port_id, destination_port_id]},
            "includes": {"id": True, "is_icd": True, "trade_id": True},
        }
    )["list"]
    origin_port = destination_port = {}

    for data in locations_list:
        if data["id"] == origin_port_id:
            origin_port = data
        elif data["id"] == destination_port_id:
            destination_port = data

    return origin_port, destination_port


def get_port_pairs_hash(
    origin_port, destination_port, all_rates, origin_port_id, destination_port_id
):
    updated_list = []

    for data in all_rates:
        if not data:
            continue
        if origin_port["is_icd"] and not data["origin_main_port_id"]:
            continue
        if not origin_port["is_icd"] and data["origin_main_port_id"]:
            continue
        if destination_port["is_icd"] and not data["destination_main_port_id"]:
            continue
        if not destination_port["is_icd"] and data["destination_main_port_id"]:
            continue
        if not data["shipping_line_id"]:
            continue
        if not data["service_provider_id"]:
            continue
        if not data["destination_detention"]["free_limit"]:
            continue

        if data["source"] == "spot_negotiation_rate":
            for freight_object in data["freights"]:
                freight_object["validity_start"] = datetime.strptime(
                    freight_object["validity_start"].split("T")[0], "%Y-%m-%d"
                ).date()
                freight_object["validity_end"] = datetime.strptime(
                    freight_object["validity_end"].split("T")[0], "%Y-%m-%d"
                ).date()

        updated_list.append(data)
    all_rates = updated_list
    port_pairs = {}

    for row in all_rates:
        row_origin_port_id = (
            row["origin_main_port_id"] if origin_port["is_icd"] else origin_port_id
        )
        row_destination_port_id = (
            row["destination_main_port_id"]
            if destination_port["is_icd"]
            else destination_port_id
        )

        key = f"{row_origin_port_id}_{row_destination_port_id}"
        if key not in port_pairs:
            port_pairs[key] = []
        port_pairs[key].append(row["shipping_line_id"])

    return port_pairs


def format_rate_cards_params(fcl_freight_rate_cards_params):
    fcl_freight_rate_cards_params = handle_empty_ids(fcl_freight_rate_cards_params)

    try:
        fcl_freight_rate_cards_params["validity_start"] = datetime.fromisoformat(
            fcl_freight_rate_cards_params["validity_start"]
        ).date()
        fcl_freight_rate_cards_params["validity_end"] = datetime.fromisoformat(
            fcl_freight_rate_cards_params["validity_end"]
        ).date()
    except:
        fcl_freight_rate_cards_params["validity_start"] = (
            datetime.now() + timedelta(days=2)
        ).date()
        fcl_freight_rate_cards_params["validity_end"] = (
            datetime.now() + timedelta(days=30)
        ).date()

    return fcl_freight_rate_cards_params


def get_fcl_freight_rate_cards_with_schedules(
    spot_negotiation_rates, fcl_freight_rate_cards_params, sailing_schedules_required
):
    """
    Get FCL (Full Container Load) freight rate cards with associated schedules.
    Returns:
        dict: FCL freight rate cards with associated schedules.
    Process:
    1. Format the FCL freight rate cards parameters.
    2. Extract relevant parameters, including origin and destination details, and importer/exporter information.
    3. Fetch all relevant FCL freight rate cards, combining spot negotiation rates and retrieved data.
    4. Create a hash of port pairs and shipping lines for later reference.
    5. If sailing schedules are required:
       a. Fetch sailing schedules data using multithreading for each port pair and associated shipping lines.
       b. Create a hash of sailing schedules data.
    6. Initialize an empty list for fake schedules.
    7. Initialize a dictionary to store grouped rate data.
    8. Iterate through all rates:
       a. Fetch relevant schedules data, either from real sailing schedules or fake schedules.
       b. Extract freight data for the rate, including price and local costs.
       c. Update the grouping with the new data, considering currency conversion, schedule validity, and cost factors.
    9. Collect the grouped rates' data and return it.
    The function retrieves FCL freight rate cards, associates them with sailing schedules if required, and groups them based on specified criteria.
    """
    try:
        fcl_freight_rate_cards_params = format_rate_cards_params(
            fcl_freight_rate_cards_params
        )

        origin_port_id = fcl_freight_rate_cards_params["origin_port_id"]
        origin_country_id = fcl_freight_rate_cards_params["origin_country_id"]
        destination_port_id = fcl_freight_rate_cards_params["destination_port_id"]
        destination_country_id = fcl_freight_rate_cards_params["destination_country_id"]
        importer_exporter_id = fcl_freight_rate_cards_params["importer_exporter_id"]
        validity_start = fcl_freight_rate_cards_params["validity_start"]

        origin_port, destination_port = get_location_data(
            origin_port_id, destination_port_id
        )
        origin_trade_id = origin_port.get("trade_id")
        destination_trade_id = destination_port.get("trade_id")

        response = get_fcl_freight_rate_cards(fcl_freight_rate_cards_params)
        all_rates = spot_negotiation_rates + response["list"]
        all_rates = list(filter(None, all_rates))
        port_pairs = get_port_pairs_hash(
            origin_port,
            destination_port,
            all_rates,
            origin_port_id,
            destination_port_id,
        )

        fake_schedules = []
        sailing_schedules_hash = {}

        if sailing_schedules_required:
            sailing_schedules = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                executors = [
                    executor.submit(
                        get_sailing_schedules_data,
                        port_pair,
                        shipping_line,
                        validity_start,
                    )
                    for port_pair, shipping_line in port_pairs.items()
                ]

            for executor in executors:
                results = executor.result()
                sailing_schedules.extend(results)

            sailing_schedules_hash = generate_sailing_schedules_hash(sailing_schedules)

            rates = []
            data = {
                "origin_port_id": origin_port_id,
                "origin_trade_id": origin_trade_id,
                "origin_country_id": origin_country_id,
                "destination_port_id": destination_port_id,
                "destination_trade_id": destination_trade_id,
                "destination_country_id": destination_country_id,
            }

            response = schedule_client.get_fake_sailing_schedules(data)
            fake_schedules = response["list"]

        params = {
            "origin_port_id": origin_port_id,
            "destination_port_id": destination_port_id,
        }
        predicted_transit_time = schedule_client.get_predicted_transit_time(params)

        grouping = {}
        selected_schedule_ids = set(
            [
                freight.get("schedule_id")
                for data in all_rates
                for freight in data["freights"]
                if freight.get("schedule_id")
            ]
        )

        for data in all_rates:
            data_schedules = get_relevant_schedules(
                data,
                origin_port,
                destination_port,
                origin_port_id,
                destination_port_id,
                sailing_schedules_hash,
            )

            if not data_schedules:
                data_schedules = fake_schedules

            data_schedules = list(data_schedules)
            freights = get_freights(
                data,
                sailing_schedules_required,
                data_schedules,
                predicted_transit_time,
                selected_schedule_ids,
            )

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
                        "organization_id": importer_exporter_id,
                    }
                ).get("price")
                for line_item in (
                    data.get("origin_local", {}).get("line_items", [])
                    + data.get("destination_local", {}).get("line_items", [])
                )
            )

            detention_free_limit = int(
                data["destination_detention"].get("free_limit", 0)
            )
            grouping = update_grouping(
                data,
                currency,
                locals_price,
                sailing_schedules_required,
                detention_free_limit,
                grouping,
                importer_exporter_id,
            )

        rates = [v["data"] for v in grouping.values()]

        return {"list": rates}

    except Exception as e:
        traceback.print_exc()
        sentry_sdk.capture_exception(e)
        print(e, "Error In Fcl Freight Rate Cards Schedules")
        return {"list": []}
