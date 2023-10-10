from configs.env import *
from services.bramhastra.client import ClickHouse
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.constants import INDIAN_LOCATION_ID
from services.bramhastra.database.dictionaries.country_rate_count import (
    CountryRateCount,
)
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)
from services.bramhastra.models.fcl_freight_rate_audit_statistic import (
    FclFreightRateAuditStatistic,
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from database.db_session import db
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import (
    FeedbackFclFreightRateStatistic,
)
from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import (
    SpotSearchFclFreightRateStatistic,
)
from services.bramhastra.models.checkout_fcl_freight_rate_statistic import (
    CheckoutFclFreightRateStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.models.data_migration import DataMigration
from services.bramhastra.models.air_freight_rate_statistic import (
    AirFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_action import FclFreightAction
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.models.fcl_freight_rate_request_statistics import (
    FclFreightRateRequestStatistic,
)
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import (
    FeedbackFclFreightRateStatistic,
)
from database.create_clicks import Clicks
from database.db_session import db


def main():
    print("running migration")
    db.execute_sql(f"DROP TABLE {FclFreightAction._meta.table_name}")
    db.execute_sql(f"DROP TABLE {ShipmentFclFreightRateStatistic._meta.table_name}")
    db.execute_sql(f"DROP TABLE {FclFreightRateRequestStatistic._meta.table_name}")
    db.execute_sql(f"DROP TABLE {FclFreightRateRequestStatistic._meta.table_name}")
    db.create_tables(
        [
            FclFreightAction,
            ShipmentFclFreightRateStatistic,
            FeedbackFclFreightRateStatistic,
            FclFreightRateRequestStatistic,
        ]
    )
    try:
        db.create_tables(
            [
                FclFreightAction,
                FclFreightRateAuditStatistic,
                AirFreightRateStatistic,
                FclFreightRateRequestStatistic,
                FclFreightRateStatistic,
                FeedbackFclFreightRateStatistic,
                SpotSearchFclFreightRateStatistic,
                CheckoutFclFreightRateStatistic,
                ShipmentFclFreightRateStatistic,
                DataMigration,
                FclFreightAction,
            ]
        )
    except Exception:
        pass

    click = ClickHouse()

    try:
        click.execute("drop database brahmastra")
    except Exception:
        pass

    click.execute("create database brahmastra")

    Clicks(
        dictionaries=[CountryRateCount],
        models=[
            FeedbackFclFreightRateStatistic,
            FclFreightRateAuditStatistic,
            AirFreightRateStatistic,
            FclFreightRateStatistic,
            FclFreightRateRequestStatistic,
            FclFreightAction,
        ],
        ignore_oltp=True,
    ).create()

    print("started inserting fcl")

    execute_fcl(click)

    print("started inserting air")

    execute_air(click)

    db.execute_sql(f"ALTER TABLE fcl_freight_actions REPLICA IDENTITY FULL;")
    db.execute_sql(f'ALTER TABLE fcl_freight_rate_request_statistics REPLICA IDENTITY FULL;')
    db.execute_sql(f'ALTER TABLE feedback_fcl_freight_rate_statistics REPLICA IDENTITY FULL;')


def execute_fcl(click):
    init_query = f"""INSERT 
    INTO 
    brahmastra.{FclFreightRateStatistic._meta.table_name} 
    (applicable_destination_local_count,applicable_origin_local_count,bas_currency,bas_price,bas_standard_price,bas_standard_price_accuracy,bas_standard_price_diff_from_selected_rate,bookings_created,bulk_operation_id,checkout_count,cogo_entity_id,commodity,container_size,container_type,containers_count,created_at,currency,destination_continent_id,destination_country_id,destination_demurrage_id,destination_detention_id,destination_local_id,destination_main_port_id,destination_port_id,destination_pricing_zone_map_id,destination_region_id,destination_trade_id,dislikes_count,id,identifier,is_deleted,last_action,likes_count,market_price,mode,operation_created_at,operation_updated_at,origin_continent_id,origin_country_id,origin_demurrage_id,origin_detention_id,origin_local_id,origin_main_port_id,origin_port_id,origin_pricing_zone_map_id,origin_region_id,origin_trade_id,parent_mode,parent_rate_id,parent_rate_mode,parent_validity_id,payment_term,performed_by_id,performed_by_type,price,procured_by_id,rate_created_at,rate_id,rate_sheet_id,rate_type,rate_updated_at,revenue_desk_visit_count,schedule_type,service_provider_id,shipment_cancelled,shipment_completed,shipping_line_id,sign,so1_select_count,so1_visit_count,source,source_id,sourced_by_id,spot_search_count,standard_price,status,tag,updated_at,validity_created_at,validity_end,validity_id,validity_start,validity_updated_at,version) 
    SETTINGS async_insert=1, wait_for_async_insert=1 
    SELECT applicable_destination_local_count,applicable_origin_local_count,bas_currency,bas_price,bas_standard_price,0,bas_standard_price_diff_from_selected_rate,bookings_created,bulk_operation_id,checkout_count,cogo_entity_id,commodity,container_size,container_type,containers_count,created_at,currency,destination_continent_id,destination_country_id,destination_demurrage_id,destination_detention_id,destination_local_id,destination_main_port_id,destination_port_id,destination_pricing_zone_map_id,destination_region_id,destination_trade_id,dislikes_count,id,identifier,is_deleted,last_action,likes_count,market_price,mode,operation_created_at,operation_updated_at,origin_continent_id,origin_country_id,origin_demurrage_id,origin_detention_id,origin_local_id,origin_main_port_id,origin_port_id,origin_pricing_zone_map_id,origin_region_id,origin_trade_id,parent_mode,parent_rate_id,parent_rate_mode,parent_validity_id,payment_term,performed_by_id,performed_by_type,price,procured_by_id,rate_created_at,rate_id,rate_sheet_id,rate_type,rate_updated_at,revenue_desk_visit_count,schedule_type,service_provider_id,shipment_cancelled,shipment_completed,shipping_line_id,1,so1_select_count,so1_visit_count,source,source_id,sourced_by_id,spot_search_count,standard_price,status,tag,updated_at,validity_created_at,validity_end,validity_id,validity_start,validity_updated_at,toUnixTimestamp64Milli(operation_updated_at) FROM postgresql('{DATABASE_HOST}:{DATABASE_PORT}', '{DATABASE_NAME}', 'fcl_freight_rate_statistics_temp', '{DATABASE_USER}', '{DATABASE_PASSWORD}')"""
    click.execute(init_query + " WHERE rate_type != 'cogo_assured'")
    print("done cogoassured")
    click.execute(
        init_query
        + f" WHERE rate_type = 'cogo_assured' AND origin_country_id = '{INDIAN_LOCATION_ID}'"
    )
    print("done cogo assured origin india")
    click.execute(
        init_query
        + f" WHERE rate_type = 'cogo_assured' AND origin_country_id != '{INDIAN_LOCATION_ID}'"
    )
    print("done cogo assured non origin india")


def execute_air(click):
    columns = [field for field in AirFreightRateStatistic._meta.fields.keys()]
    fields = ",".join(columns)
    for source in ["manual", "predicted", "rate_extension", "rate_sheet"]:
        click.execute(
            f"INSERT INTO brahmastra.{AirFreightRateStatistic._meta.table_name} SETTINGS async_insert=1, wait_for_async_insert=1 SELECT {fields} FROM postgresql('{DATABASE_HOST}:{DATABASE_PORT}', '{DATABASE_NAME}', '{AirFreightRateStatistic._meta.table_name}', '{DATABASE_USER}', '{DATABASE_PASSWORD}') WHERE source = %(source)s",
            {"source": source},
        )
        print("done with source: ", source)


if __name__ == "__main__":
    main()
