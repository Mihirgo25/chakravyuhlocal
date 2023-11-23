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
from configs.global_constants import CONTAINER_TYPES, ALL_COMMODITIES, CONTAINER_SIZES
from configs.fcl_freight_rate_constants import CRITICAL_PORTS_INDIA_VIETNAM
from services.fcl_freight_rate.helpers.get_critical_ports_extension_parameters import (
    fetch_all_base_port_ids,
)
from database.rails_db import get_ff_mlo


def apply_filter(df, container_type, commodity):
    filtered_df = df[
        (df["container_type"] == container_type) & (df["commodity"] == commodity)
    ]
    return filtered_df


def get_weighted_average(df, ln):
    """
    Weighted Ratio = 
    Total Data Points for Three Months
    ((1st Month Ratio × 1st Month Data Points) + 
    (2nd Month Ratio × 2nd Month Data Points) + 
    (3rd Month Ratio × 3rd Month Data Points)) / Total Data Points
    
    Parameters:
    - df: DataFrame
    - ln: Length

    Returns:
    - None
    """
    weighted_sum = 0
    total = 0
    for i in range(ln):
        weighted_sum = weighted_sum + (
            df["freq_{}".format(i)] * df["ratio_{}".format(i)]
        )
        total = total + df["freq_{}".format(i)]

    weighted_ratio = weighted_sum / total
    df["weighted_ratio"] = weighted_ratio


def get_iqr_lower_upper_bound(df):
    """
    Calculates the lower and upper bounds for outliers using Interquartile Range (IQR).

    Parameters:
    - df: DataFrame

    Returns:
    - Tuple: (lower_bound, upper_bound)
    """
    Q1 = df["price"].quantile(0.25)
    Q3 = df["price"].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    return lower_bound, upper_bound


def currency_exchange_to_usd(df):
    unique_currencies = df['currency'].unique()
    currency_rate_mappings = {}
    for currency in unique_currencies:
        if currency != 'USD':
            data = {"from_currency": currency, "to_currency": "USD", "price": "1"}
            resp = common.get_money_exchange_for_fcl(data)
            conversion_rate = resp.get("rate") or resp["price"] / float(data["price"])
            currency_rate_mappings['currency'] = conversion_rate
            
    def convert_currency(row):
        if row["currency"] != "USD":
            conversion_rate = currency_rate_mappings[row["currency"]]
            row["price"] *= conversion_rate
            row["currency"] = "USD"
        return row

    df = df.apply(convert_currency, axis=1)

    return df


def data_cleaning(df):
    """
    Cleans the DataFrame by extracting price and currency information from line items.

    Parameters:
    - df: DataFrame

    Returns:
    - DataFrame: Cleaned DataFrame
    """
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
    """
    Retrieves data for previous months based on specified parameters.

    Parameters:
    - origin_port_id: str
    - destination_port_id: str
    - container_size: str
    - current_time: datetime

    Returns:
    - List: List of DataFrames for previous months
    """
    previous_months_data = []
    ff_mlo = get_ff_mlo()

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
                FclFreightRate.origin_port_id == origin_port_id,
                FclFreightRate.destination_port_id == destination_port_id,
                FclFreightRate.container_size == container_size,
                FclFreightRateAudit.action_name.in_(["create", "update"]),
                FclFreightRateAudit.created_at >= start_time,
                FclFreightRateAudit.created_at <= end_time,
                ~(
                    FclFreightRate.mode.in_(
                        [
                            "predicted",
                            "cluster_extension",
                            "cogolens",
                            "rate_manufactured",
                        ]
                    )
                ),
                FclFreightRate.service_provider.in_(ff_mlo),
                FclFreightRate.rate_type == DEFAULT_RATE_TYPE,
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
    """
    Calculating ratios for each shipping line per month, as we consider a span of 3 months (or 2 months) to compute the weighted ratio. The calculated ratios are then saved to the database.

    Parameters:
    - origin_port_id: str
    - destination_port_id: str
    - container_size: str
    - current_time: datetime

    Returns:
    - None
    """
    previous_months_data = get_previous_months_data(
        origin_port_id, destination_port_id, container_size, current_time
    )

    if len(previous_months_data) < 2:
        return

    for commodity in ALL_COMMODITIES:
        for container_type in CONTAINER_TYPES:
            updated_previous_months_dfs = []
            for temp_df in previous_months_data:
                df = apply_filter(temp_df, container_type, commodity)

                if len(df[df["currency"] != "USD"]) > 0:
                    df = currency_exchange_to_usd(df)

                lower_bound, upper_bound = get_iqr_lower_upper_bound(df)

                if math.isnan(lower_bound) or math.isnan(upper_bound):
                    print("nan value encountered while calculating IQR")
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
                cur_df = cur_df[
                    cur_df["shipping_line_id"] != "e6da6a42-cc37-4df2-880a-525d81251547"
                ]
                cur_df = cur_df.reset_index(drop=True)
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

            all_unique_shipping_line_ids = set(
                flattened_shipping_line_id_frequencies_list
            )

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
                        freqs[i].append(
                            shipping_line_id_frequencies_list[i][shipping_line_id]
                        )

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


def populate_fcl_freight_rate_estimation_ratio():
    """
    Calculate the weighted ratio for shipping lines associated with specified origin and destination port pairs. This calculation will be utilized subsequently to estimate BAS prices for shipping lines lacking available data. This process is applicable for both China to India and India to China trade line. Utilizes concurrent execution with a ThreadPoolExecutor for efficient processing.

    Parameters:
    - None

    Returns:
    - None
    """
    # all critical ports combinations
    critical_origin_port_ids = CRITICAL_PORTS_INDIA_VIETNAM
    critical_destination_port_ids = fetch_all_base_port_ids()

    origin_destination_port_pairs = []

    for origin_port_id in critical_origin_port_ids:
        for destination_port_id in critical_destination_port_ids:
            origin_destination_port_pairs.append((origin_port_id, destination_port_id))

    for origin_port_id in critical_destination_port_ids:
        for destination_port_id in critical_origin_port_ids:
            origin_destination_port_pairs.append((origin_port_id, destination_port_id))

    current_time = datetime.now()
    for origin_port_id, destination_port_id in origin_destination_port_pairs:
        for container_size in CONTAINER_SIZES:
            process_container_size(origin_port_id, destination_port_id, container_size, current_time)
