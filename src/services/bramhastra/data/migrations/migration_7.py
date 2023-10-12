import csv
from services.bramhastra.client import ClickHouse
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)

CLICKHOUSE_CSV_PATH = ""

REQUIRED_COLUMNS = [
    "id",
    "identifier",
    "validity_id",
    "rate_id",
    "payment_term",
    "schedule_type",
    "origin_port_id",
    "destination_port_id",
    "origin_main_port_id",
    "destination_main_port_id",
    "origin_region_id",
    "destination_region_id",
    "origin_country_id",
    "destination_country_id",
    "origin_continent_id",
    "destination_continent_id",
    "origin_trade_id",
    "destination_trade_id",
    "origin_pricing_zone_map_id",
    "destination_pricing_zone_map_id",
    "price",
    "standard_price",
    "market_price",
    "validity_start",
    "validity_end",
    "currency",
    "shipping_line_id",
    "service_provider_id",
    "mode",
    "likes_count",
    "dislikes_count",
    "spot_search_count",
    "checkout_count",
    "bookings_created",
    "rate_created_at",
    "rate_updated_at",
    "validity_created_at",
    "validity_updated_at",
    "commodity",
    "container_size",
    "container_type",
    "containers_count",
    "origin_local_id",
    "destination_local_id",
    "applicable_origin_local_count",
    "applicable_destination_local_count",
    "origin_detention_id",
    "destination_detention_id",
    "origin_demurrage_id",
    "destination_demurrage_id",
    "cogo_entity_id",
    "rate_type",
    "sourced_by_id",
    "procured_by_id",
    "created_at",
    "updated_at",
    "status",
    "last_action",
    "parent_rate_id",
    "parent_validity_id",
    "so1_select_count",
    "parent_mode",
    "source",
    "source_id",
    "performed_by_id",
    "performed_by_type",
    "rate_sheet_id",
    "bulk_operation_id",
    "operation_created_at",
    "operation_updated_at",
    "is_deleted",
    "bas_price",
    "bas_standard_price",
    "bas_currency",
    "tag",
    "shipment_completed",
    "shipment_cancelled",
    "bas_standard_price_accuracy",
    "bas_standard_price_diff_from_selected_rate",
    "parent_rate_mode",
    "revenue_desk_visit_count",
    "so1_visit_count",
]


def get_data_from_clickhouse():
    # click.execute(f"SELECT * FROM brahmastra.{FclFreightRateStatistic._meta.table_name} INTO OUTFILE 'output.csv' FORMAT CSVWithNames")
    data = []

    with open(CLICKHOUSE_CSV_PATH, "r") as inputFile:
        for row in csv.reader(inputFile):
            data.append(row)

    return data


def get_column_mapping(column_names):
    column_mapping = {}

    for req_col in enumerate(REQUIRED_COLUMNS):
        column_mapping[req_col] = -1
        for col_idx, col_name in enumerate(column_names):
            if col_name == req_col:
                column_mapping[req_col] = col_idx

    return column_mapping


def refactor_data_for_insertion(data):
    new_table = [REQUIRED_COLUMNS]
    column_mapping = get_column_mapping(data[0])

    for row in data[1:]:
        new_row = []
        for req_col in REQUIRED_COLUMNS:
            mp_idx = column_mapping[req_col]
            if mp_idx != -1:
                new_row.append(row[mp_idx])
            else:
                new_row.append("DEFAULT")
        new_table.append(new_row)

    return new_table


def insert_into_clickhouse(click, insert_query, bulk_data):
    values = []
    for row in bulk_data:
        data_str = "','".join(row)
        data_str = "('" + data_str + "')"
        values.append(data_str)
    values = ",".join(values)

    insert_query = insert_query + values + ";"

    click.execute(insert_query)


if __name__ == "__main__":
    data = get_data_from_clickhouse()
    final_table = refactor_data_for_insertion(data)

    click = ClickHouse()
    column_names = ",".join(REQUIRED_COLUMNS)

    insert_query = f"INSERT INTO brahmastra.{FclFreightRateStatistic._meta.table_name} ({column_names}) VALUES "

    batch_size = 100
    bulk_data = []

    for idx, row in enumerate(final_table):
        bulk_data.append(row)

        if (len(bulk_data) >= batch_size) or (idx == (len(final_table) - 1)):
            insert_into_clickhouse(click, insert_query, bulk_data)
            bulk_data = []
