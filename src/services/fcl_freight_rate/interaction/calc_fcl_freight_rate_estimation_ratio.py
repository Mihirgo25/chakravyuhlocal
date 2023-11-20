import math
import json
import pandas as pd
import concurrent.futures

from datetime import datetime, timedelta
from micro_services.client import common
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.fcl_freight_rate.interaction.create_fcl_freight_rate_estimation_ratio import (
    create_fcl_freight_rate_estimation_ratio,
)

container_sizes = [
    "20", 
    "40", 
    "40HC", 
    "45HC"
]

container_types = [
    "standard",
    "refer",
    "open_top",
    "open_side",
    "flat_rack",
    "iso_tank",
]

commodities = [
    "agro",
    "chilled",
    "corrosives-8",
    "cotton_and_yarn",
    "emit_flammable_gases_with_water-4.3",
    "fabric_and_textiles",
    "flammable_liquids-3",
    "flammable_solids-4.1",
    "flammable_solids_self_heat-4.2",
    "frozen",
    "gases-2.1",
    "gases-2.2",
    "gases-2.3",
    "general",
    "imo_classes-5.1",
    "in_gauge_cargo",
    "infectious_substances-6.2",
    "miscellaneous_dangerous_goods-9",
    "non_haz_solids",
    "pharma",
    "pta",
    "radioactive_material-7",
    "sugar_rice",
    "toxic_substances-6.1",
    "white_goods",
]


def apply_filter(df, container_type, commodity):
    filtered_df = df[
        (df["container_type"] == container_type) & (df["commodity"] == commodity)
    ]
    return filtered_df


def get_weighted_average(df, ln):
    mult = 0
    total = 0
    for i in range(ln):
        mult = mult + (df["freq_{}".format(i)] * df["ratio_{}".format(i)])
        total = total + df["freq_{}".format(i)]

    mult_by_total = mult / total
    df["weighted_ratio"] = mult_by_total


def get_iqr_lower_upper_bound(df):
    Q1 = df["price"].quantile(0.25)
    Q3 = df["price"].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    return lower_bound, upper_bound


def currency_exchange_to_usd(df):
    data = {"from_currency": "INR", "to_currency": "USD", "price": "1"}
    resp = common.get_money_exchange_for_fcl(data)
    conversion_rate = resp.get("rate") or resp["price"] / float(data["price"])

    def convert_currency(row):
        if row["currency"] == "INR":
            row["price"] *= conversion_rate
            row["currency"] = "USD"
        return row

    df = df.apply(convert_currency, axis=1)

    return df


def data_cleaning(df):
    price = []
    currency = []
    for i in range(df.shape[0]):
        try:
            line_items_list = json.loads(df["line_items"][i])

            flag = False
            for line_item in line_items_list:
                if line_item["code"] == "BAS":
                    flag = True
                    price.append(line_item["price"])
                    currency.append(line_item["currency"])

            if not flag:
                price.append(None)
                currency.append(None)
                
        except Exception as e:
            print(f"Error processing line_items at index {i}: {e}")
            price.append(None)
            currency.append(None)

    df["price"] = price
    df["currency"] = currency
    df.drop(columns=["line_items"], inplace=True)
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


def get_previous_months_data(
    origin_port_id, destination_port_id, container_size, current_time
):
    previous_months_data = []

    for days in [30, 60, 90]:
        start_time = current_time - timedelta(days=days)
        end_time = start_time + timedelta(days=30)

        query = (
            FclFreightRate.select(
                FclFreightRateAudit.data["line_items"].alias("line_items"),
                FclFreightRate.origin_port_id,
                FclFreightRate.destination_port_id,
                FclFreightRate.commodity,
                FclFreightRate.container_size,
                FclFreightRate.container_type,
                FclFreightRate.shipping_line_id,
            )
            .join(
                FclFreightRateAudit,
                on=(FclFreightRate.id == FclFreightRateAudit.object_id),
            )
            .where(
                (FclFreightRate.origin_port_id == origin_port_id),
                (FclFreightRate.destination_port_id == destination_port_id),
                (FclFreightRate.container_size == container_size),
                (FclFreightRateAudit.action_name.in_(["create", "update"])),
                (FclFreightRateAudit.created_at >= start_time),
                (FclFreightRateAudit.created_at <= end_time),
                ~(FclFreightRate.mode.in_(["predicted", "cluster_extension", "cogolens"])),
                (FclFreightRate.rate_type == DEFAULT_RATE_TYPE),
                ~FclFreightRate.service_provider["category_types"].contains("nvocc")
            )
        )

        records = list(query)

        data = [
            {
                "line_items": record.line_items,
                "origin_port_id": record.origin_port_id,
                "destination_port_id": record.destination_port_id,
                "commodity": record.commodity,
                "container_type": record.container_type,
                "container_size": record.container_size,
                "shipping_line_id": record.shipping_line_id,
            }
            for record in records
        ]

        df = pd.DataFrame.from_records(data)

        if df.shape[0] != 0:
            df = data_cleaning(df)
            if df.shape[0] != 0:
                previous_months_data.append(df)

    return previous_months_data


def process_container_size(
    origin_port_id, destination_port_id, container_size, current_time
):
    previous_months_data = get_previous_months_data(
        origin_port_id, destination_port_id, container_size, current_time
    )

    if len(previous_months_data) < 2:
        return

    for commodity in commodities:
        for container_type in container_types:
            updated_previous_months_dfs = []
            for temp_df in previous_months_data:
                df = apply_filter(temp_df, container_type, commodity)

                if len(df[df["currency"] == "INR"]) > 0:
                    df = currency_exchange_to_usd(df)
                    
                lower_bound, upper_bound = get_iqr_lower_upper_bound(df)
                
                if math.isnan(lower_bound) or math.isnan(upper_bound):
                    print('nan value encountered while calculating IQR')
                    continue

                new_df = df[(df["price"] >= lower_bound) & (df["price"] <= upper_bound)]
                new_df.reset_index(drop=True, inplace=True)

                if new_df.shape[0] != 0:
                    updated_previous_months_dfs.append(new_df)

            if len(updated_previous_months_dfs) < 2:
                continue

            shipping_line_id_frequencies_list = []
            ratios_for_each_shipping_line_id_list = []

            for cur_df in updated_previous_months_dfs:
                df_avg = cur_df.groupby("shipping_line_id")["price"].mean()
                df_avg = pd.DataFrame(df_avg)

                shipping_line_id_frequencies = cur_df["shipping_line_id"].value_counts()
                shipping_line_id_frequencies = shipping_line_id_frequencies.to_dict()

                median_of_avg_price = df_avg["price"].median()

                ratios_for_each_shipping_line_id = df_avg / median_of_avg_price

                shipping_line_id_frequencies_list.append(shipping_line_id_frequencies)
                ratios_for_each_shipping_line_id_list.append(
                    ratios_for_each_shipping_line_id
                )

            flattened_shipping_line_id_frequencies_list = [
                shipping_line_id
                for shipping_line_id_frequencies in shipping_line_id_frequencies_list
                for shipping_line_id in shipping_line_id_frequencies
            ]

            all_unique_shipping_line_ids = set(flattened_shipping_line_id_frequencies_list)

            shipping_line_ids = []
            ratios = [[] for _ in range(3)]
            freqs = [[] for _ in range(3)]

            for shipping_line_id in all_unique_shipping_line_ids:
                flag = True
                for (
                    ratios_for_each_shipping_line_id
                ) in ratios_for_each_shipping_line_id_list:
                    if shipping_line_id in ratios_for_each_shipping_line_id.index:
                        flag = flag and True
                    else:
                        flag = flag and False

                if flag:
                    shipping_line_ids.append(shipping_line_id)
                    for i in range(len(ratios_for_each_shipping_line_id_list)):
                        ratios[i].append(
                            ratios_for_each_shipping_line_id_list[i].to_dict()["price"][
                                shipping_line_id
                            ]
                        )
                        freqs[i].append(shipping_line_id_frequencies_list[i][shipping_line_id])

            new_df = pd.DataFrame()
            new_df["origin_port_id"] = [origin_port_id] * len(shipping_line_ids)
            new_df["destination_port_id"] = [destination_port_id] * len(
                shipping_line_ids
            )
            new_df["commodity"] = [commodity] * len(shipping_line_ids)
            new_df["container_size"] = [container_size] * len(shipping_line_ids)
            new_df["container_type"] = [container_type] * len(shipping_line_ids)
            new_df["shipping_line_id"] = shipping_line_ids

            for i in range(len(ratios_for_each_shipping_line_id_list)):
                new_df["ratio_{}".format(i)] = ratios[i]
                new_df["freq_{}".format(i)] = freqs[i]

            get_weighted_average(new_df, len(updated_previous_months_dfs))

            for row in new_df.itertuples(index=False):
                request = {
                    "origin_port_id": row.origin_port_id,
                    "destination_port_id": row.destination_port_id,
                    "commodity": row.commodity,
                    "container_size": row.container_size,
                    "container_type": row.container_type,
                    "shipping_line_id": row.shipping_line_id,
                    "weighted_ratio": row.weighted_ratio,
                }
                create_fcl_freight_rate_estimation_ratio(request)


def fcl_freight_rate_estimation_ratio():
    # india to china and china to india trade lines
    critical_origin_port_ids = [
        "eb187b38-51b2-4a5e-9f3c-978033ca1ddf",
        "7aa6ac82-c295-497f-bfe1-90294cdfa7a9",
        "3c843f50-867c-4b07-bb57-e61af97dabfe",
    ]
    critical_destination_port_ids = [
        "23630ba9-b478-4000-ba75-05606d72d19f",
        "2b318074-ad35-41e9-bb00-68d27a47ec47",
        "33470eb3-0a63-4427-bf7e-b68d043364dc",
        "6eb66c1b-9348-4fb9-a9e7-37c5d153272e",
        "762ea6af-c125-48cd-9b40-cf0539bd55ca",
        "79b677ac-e075-47a4-8f99-bfa2cda5e55b",
        "83da7f49-f04c-4c05-b967-346bc7d528f8",
        "c47b8ce8-4110-4a33-a98f-d1e83ba83779",
    ]

    origin_destination_port_pairs = []

    for origin_port_id in critical_origin_port_ids:
        for destination_port_id in critical_destination_port_ids:
            origin_destination_port_pairs.append((origin_port_id, destination_port_id))

    for origin_port_id in critical_destination_port_ids:
        for destination_port_id in critical_origin_port_ids:
            origin_destination_port_pairs.append((origin_port_id, destination_port_id))

    current_time = datetime.now()
    for origin_port_id, destination_port_id in origin_destination_port_pairs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(
                    process_container_size,
                    origin_port_id,
                    destination_port_id,
                    "20",
                    current_time,
                ),
                executor.submit(
                    process_container_size,
                    origin_port_id,
                    destination_port_id,
                    "40",
                    current_time,
                ),
                executor.submit(
                    process_container_size,
                    origin_port_id,
                    destination_port_id,
                    "40HC",
                    current_time,
                ),
                executor.submit(
                    process_container_size,
                    origin_port_id,
                    destination_port_id,
                    "45HC",
                    current_time,
                ),
            ]