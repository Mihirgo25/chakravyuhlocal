from datetime import datetime, timedelta
from services.fcl_freight_rate.models.critical_port_trend_indexes import (
    CriticalPortTrendIndex,
)
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.bramhastra.interactions.list_fcl_freight_rate_statistics import (
    list_fcl_freight_rate_statistics,
)
from services.fcl_freight_rate.helpers.rate_extension_via_bulk_operation import (
    rate_extension_via_bulk_operation,
)
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from micro_services.client import common
from fastapi.encoders import jsonable_encoder


def get_filters(start_time, query_type, rate_ids):
    return {
        "updated_at_less_than": start_time,
        "query_type": query_type,
        "rate_id": rate_ids,
        "validity_end_greater_than": datetime.now().date() + timedelta(days=1),
        "group_by": ["shipping_line_id"],
        "rate_type": DEFAULT_RATE_TYPE,
        "parent_mode": "supply",
    }


def get_shipping_line_dict():
    return {"20": None, "40": None, "40HC": None}


async def update_cluster_extension_by_latest_trends(request):
    start_time = request.get("start_time")
    origin_port_id = request["origin_port_id"]
    destination_port_id = request["destination_port_id"]

    (
        min_decrease_percent,
        max_increase_percent,
        min_decrease_markup,
        max_increase_markup,
        approval_status,
        manual_gri,
    ) = get_record_details(origin_port_id, destination_port_id)

    if not approval_status:
        return

    if manual_gri:
        overall_gri_avg = manual_gri
    else:
        freight_rates = get_freight_rates(request)
        shipping_line_gri_mapping = {}
        for container_size in ["20", "40", "40HC"]:
            rates = [
                rate
                for rate in freight_rates
                if rate["container_size"] == container_size
            ]
            if not rates:
                continue
            prices = []
            rate_ids = []
            shipping_line_ids = []

            for rate in rates:
                rate_ids.append(rate["id"])
                shipping_line_ids.append(rate["shipping_line_id"])

                price, count = get_bas_price(rate["validities"])
                if price and count:
                    prices.append(price / count)

            response = await list_fcl_freight_rate_statistics(
                get_filters(start_time, "average_price", rate_ids),
                1000,
                1,
                False,
            )

            if not response.get("list"):
                continue

            prev_avg_mapping = {
                row["shipping_line_id"]: row["average_standard_price"]
                for row in response["list"]
                if row.get("shipping_line_id")
            }

            shipping_line_mapping = {}
            for shipping_id, price in zip(shipping_line_ids, prices):
                if shipping_id not in shipping_line_mapping:
                    shipping_line_mapping[shipping_id] = {"price": price, "total": 1}
                else:
                    shipping_line_mapping[shipping_id]["price"] += price
                    shipping_line_mapping[shipping_id]["total"] += 1

            average_prices = {}
            for shipping_id in shipping_line_mapping:
                total = shipping_line_mapping[shipping_id]["price"]
                count = shipping_line_mapping[shipping_id]["total"]
                average_prices[shipping_id] = total / count

            for shipping_line_id in average_prices.keys():
                cur = average_prices[shipping_line_id]
                prev = prev_avg_mapping.get(shipping_line_id)
                if prev and cur:
                    gri_perc = ((cur - prev) / prev) * 100
                    if shipping_line_id in shipping_line_gri_mapping.keys():
                        shipping_line_gri_mapping[shipping_line_id][
                            container_size
                        ] = gri_perc
                    else:
                        shipping_line_gri_mapping[
                            shipping_line_id
                        ] = get_shipping_line_dict()
                        shipping_line_gri_mapping[shipping_line_id][
                            container_size
                        ] = gri_perc
        shipping_line_avg_mapping = {}

        for key, sub_dict in shipping_line_gri_mapping.items():
            values = []
            for sub_key in sub_dict:
                if sub_dict[sub_key]:
                    values.append(sub_dict[sub_key])
            if values:
                average_value = sum(values) / len(values)
                shipping_line_avg_mapping[key] = average_value

        if not shipping_line_avg_mapping:
            return

        overall_gri_avg = 0
        for key in shipping_line_avg_mapping.keys():
            overall_gri_avg += shipping_line_avg_mapping[key]

        overall_gri_avg /= len(shipping_line_avg_mapping.keys())

    if overall_gri_avg and (
        min_decrease_percent <= overall_gri_avg <= max_increase_percent
    ):
        request["source"] = "cluster_extension_worker"
        request["markup"] = overall_gri_avg

        request["min_decrease_markup"] = min_decrease_markup
        request["max_increase_markup"] = max_increase_markup
        request["filters"] = {
            "origin_port_id": request.get("origin_port_id"),
            "destination_port_id": request.get("destination_port_id"),
            "rate_type": "market_place",
            "updated_at_less_than": start_time.isoformat(),
        }
        rate_extension_via_bulk_operation(request)
        request["filters"] = {
            "origin_port_id": request.get("origin_secondary_ports"),
            "destination_port_id": request.get("destination_secondary_ports"),
            "rate_type": "market_place",
            "updated_at_less_than": start_time.isoformat(),
        }
        rate_extension_via_bulk_operation(request)


def get_record_details(origin_port_id, destination_port_id):
    min_decrease_percent, max_increase_percent = -2, 5
    min_decrease_markup, max_increase_markup = -20, 50
    approval_status, manual_gri = True, None

    record = (
        CriticalPortTrendIndex.select(
            CriticalPortTrendIndex.approval_status,
            CriticalPortTrendIndex.manual_gri,
            CriticalPortTrendIndex.min_decrease_percent,
            CriticalPortTrendIndex.max_increase_percent,
            CriticalPortTrendIndex.min_decrease_markup,
            CriticalPortTrendIndex.max_increase_markup,
        ).where(
            (CriticalPortTrendIndex.destination_port_id == destination_port_id)
            & (CriticalPortTrendIndex.origin_port_id == origin_port_id)
        )
    ).first()

    if record:
        min_decrease_percent = record.min_decrease_percent
        max_increase_percent = record.max_increase_percent
        min_decrease_markup = record.min_decrease_markup
        max_increase_markup = record.max_increase_markup
        approval_status = record.approval_status
        manual_gri = record.manual_gri

        if manual_gri:
            record.manual_gri = None
            record.save()

    return (
        min_decrease_percent,
        max_increase_percent,
        min_decrease_markup,
        max_increase_markup,
        approval_status,
        manual_gri,
    )


def get_freight_rates(request):
    query = FclFreightRate.select(
        FclFreightRate.id,
        FclFreightRate.container_size,
        FclFreightRate.shipping_line_id,
        FclFreightRate.validities,
    ).where(
        FclFreightRate.updated_at > request["start_time"],
        FclFreightRate.origin_port_id == request["origin_port_id"],
        FclFreightRate.commodity == request["commodity"],
        FclFreightRate.container_type == request["container_type"],
        FclFreightRate.destination_port_id == request["destination_port_id"],
        FclFreightRate.last_rate_available_date
        > datetime.now().date() + timedelta(days=1),
        FclFreightRate.mode.not_in(["predicted", "rate_extension"]),
        FclFreightRate.rate_type == DEFAULT_RATE_TYPE,
    )
    return jsonable_encoder(list(query.dicts()))


def get_bas_price(validities=[]):
    price, count = 0, 0

    for validity in validities:
        line_items = validity.get("line_items") or []
        bas_code = [line_item for line_item in line_items if line_item["code"] == "BAS"]

        if not bas_code:
            continue

        bas_price, bas_currency = bas_code[0]["price"], bas_code[0]["currency"]

        if bas_currency != "USD":
            data = {
                "from_currency": bas_currency,
                "to_currency": "USD",
                "price": bas_price,
            }
            price_in_USD = common.get_money_exchange_for_fcl(data)["price"]
            price += price_in_USD
        else:
            price += bas_price
        count += 1

    return price, count
