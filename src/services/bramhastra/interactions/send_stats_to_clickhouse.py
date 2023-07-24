from services.bramhastra.models.fcl_freight_rate_statistic import (
    FclFreightRateStatistic,
)
from services.bramhastra.models.feedback_fcl_freight_rate_statistic import (
    FeedbackFclFreightRateStatistic,
)
from services.bramhastra.models.quotation_fcl_freight_rate_statistic import (
    QuotationFclFreightRateStatistic,
)
from services.bramhastra.models.shipment_fcl_freight_rate_statistic import (
    ShipmentFclFreightRateStatistic,
)
from services.bramhastra.models.spot_search_fcl_freight_rate_statistic import (
    SpotSearchFclFreightRateStatistic,
)
from services.bramhastra.clickhouse.connect import get_clickhouse_client
from services.bramhastra.helpers.post_fcl_freight_helper import json_encoder_for_clickhouse


def send_stats_to_clickhouse(client = get_clickhouse_client()):
    query = (
        "INSERT INTO  brahmastra.fcl_freight_rate_statistics SETTINGS async_insert=1, wait_for_async_insert=1 VALUES"
    )

    values = []
    for rate in json_encoder_for_clickhouse(list(FclFreightRateStatistic.select().dicts())):
        value = value = f"""(
    {rate['id']},
    '{rate['identifier']}',
    '{rate['validity_id']}',
    '{rate['rate_id']}',
    '{rate['payment_term']}',
    '{rate['schedule_type']}',
    {f"'{rate['origin_port_id']}'" if rate['origin_port_id'] is not None else 'NULL'},
    {f"'{rate['destination_port_id']}'" if rate['destination_port_id'] is not None else 'NULL'},
    {f"'{rate['origin_main_port_id']}'" if rate['origin_main_port_id'] is not None else 'NULL'},
    {f"'{rate['destination_main_port_id']}'" if rate['destination_main_port_id'] is not None else 'NULL'},
    {f"'{rate['origin_country_id']}'" if rate['origin_country_id'] is not None else 'NULL'},
    {f"'{rate['destination_country_id']}'" if rate['destination_country_id'] is not None else 'NULL'},
    {f"'{rate['origin_continent_id']}'" if rate['origin_continent_id'] is not None else 'NULL'},
    {f"'{rate['destination_continent_id']}'" if rate['destination_continent_id'] is not None else 'NULL'},
    {f"'{rate['origin_region_id']}'" if rate['origin_region_id'] is not None else 'NULL'},
    {f"'{rate['destination_region_id']}'" if rate['destination_region_id'] is not None else 'NULL'},
    {f"'{rate['origin_trade_id']}'" if rate['origin_trade_id'] is not None else 'NULL'},
    {f"'{rate['destination_trade_id']}'" if rate['destination_trade_id'] is not None else 'NULL'},
    {f"'{rate['origin_pricing_zone_map_id']}'" if rate['origin_pricing_zone_map_id'] is not None else 'NULL'},
    {f"'{rate['destination_pricing_zone_map_id']}'" if rate['destination_pricing_zone_map_id'] is not None else 'NULL'},
    {rate['price']},
    {rate['market_price']},
    '{rate['validity_start']}',
    '{rate['validity_end']}',
    '{rate['currency']}',
    '{rate['shipping_line_id']}',
    '{rate['service_provider_id']}',
    {rate['accuracy']},
    '{rate['mode']}',
    {rate['likes_count']},
    {rate['dislikes_count']},
    {rate['spot_search_count']},
    {rate['buy_quotations_created']},
    {rate['sell_quotations_created']},
    {rate['checkout_count']},
    {rate['bookings_created']},
    '{rate['rate_created_at']}',
    '{rate['rate_updated_at']}',
    '{rate['validity_created_at']}',
    '{rate['validity_updated_at']}',
    '{rate['commodity']}',
    '{rate['container_size']}',
    '{rate['container_type']}',
    {rate['containers_count']},
    '{rate['origin_local_id']}',
    '{rate['destination_local_id']}',
    {rate['applicable_origin_local_count']},
    {rate['applicable_destination_local_count']},
    '{rate['origin_detention_id']}',
    '{rate['destination_detention_id']}',
    '{rate['origin_demurrage_id']}',
    '{rate['destination_demurrage_id']}',
    '{rate['cogo_entity_id']}',
    '{rate['rate_type']}',
    '{rate['sourced_by_id']}',
    '{rate['procured_by_id']}',
    {rate['shipment_aborted_count']},
    {rate['shipment_cancelled_count']},
    {rate['shipment_completed_count']},
    {rate['shipment_confirmed_by_service_provider_countb']},
    {rate['shipment_awaited_service_provider_confirmation_count']},
    {rate['shipment_init_count']},
    {rate['shipment_containers_gated_in_count']},
    {rate['shipment_containers_gated_out_count']},
    {rate['shipment_vessel_arrived_count']},
    {rate['shipment_is_active_count']},
    {rate['shipment_cancellation_reason_got_a_cheaper_rate_from_my_service_provider_count']},
    {rate['shipment_booking_rate_is_too_low_count']},
    '{rate['created_at']}',
    '{rate['updated_at']}',
    {rate['version']},
    {rate['sign']},
    '{rate['status']}',
    '{rate['last_action']}',
    {rate['rate_deviation_from_booking_rate']},
    {rate['rate_deviation_from_cluster_base_rate']},
    {rate['rate_deviation_from_booking_on_cluster_base_rate']},
    {rate['rate_deviation_from_latest_booking']},
    {rate['average_booking_rate']}
)"""

        values.append(value)

    query += ", ".join(values)
    client.command(query)
    
    FclFreightRateStatistic.delete().execute()


def send_feedback_stats_to_clickhouse(client = get_clickhouse_client()):
    query = (
        "INSERT INTO  brahmastra.fcl_freight_rate_statistics SETTINGS async_insert=1, wait_for_async_insert=1 VALUES"
    )

    values = []
    for rate in json_encoder_for_clickhouse(list(FeedbackFclFreightRateStatistic.select().dicts())):
        value = value = f"""(
        {rate['id']},
        '{rate['fcl_freight_rate_statistic_id']}',
        '{rate['feedback_id']}',
        '{rate['validity_id']}',
        '{rate['rate_id']}',
        {f"'{rate['source']}'" if rate['source'] is not None else 'NULL'},
        {f"'{rate['source_id']}'" if rate['source_id'] is not None else 'NULL'},
        {f"'{rate['performed_by_id']}'" if rate['performed_by_id'] is not None else 'NULL'},
        {f"'{rate['performed_by_org_id']}'" if rate['performed_by_org_id'] is not None else 'NULL'},
        '{rate['created_at']}',
        '{rate['updated_at']},
        {f"'{rate['importer_exporter_id']}'" if rate['importer_exporter_id'] is not None else 'NULL'},
        {f"'{rate['service_provider_id']}'" if rate['service_provider_id'] is not None else 'NULL'},
        '{rate['feedback_type']}',
        {f"'{rate['closed_by_id']}'" if rate['closed_by_id'] is not None else 'NULL'},
        {rate['serial_id']},
        {rate['sign']},
        {rate['version']}
)"""
        values.append(value)
        
    query += ", ".join(values)
    client.command(query)
    
    FeedbackFclFreightRateStatistic.delete().execute()
breakpoint()
def send_quotation_stats_to_clickhouse(client=get_clickhouse_client):
    query = (
        "INSERT INTO  brahmastra.fcl_freight_rate_statistics SETTINGS async_insert=1, wait_for_async_insert=1 VALUES"
    )

    values = []
    for rate in json_encoder_for_clickhouse(list(QuotationFclFreightRateStatistic.select().dicts())):
        value = value = f"""(
        {rate['id']},
        '{rate['validity_id']}',
        '{rate['rate_id']}',
        '{rate['spot_search_id']}',
        '{rate['spot_search_fcl_customs_services_id']}',
        '{rate['checkout_id']}',
        {f"'{rate['checkout_fcl_freight_rate_services_id']}'" if rate['checkout_fcl_freight_rate_services_id'] is not None else 'NULL'},
        '{rate['sell_quotation_id']}',
        '{rate['buy_quotation_id']}',
        {f"'{rate['shipment_id']}'" if rate['shipment_id'] is not None else 'NULL'},
        {f"'{rate['shipment_fcl_freight_rate_services_id']}'" if rate['shipment_fcl_freight_rate_services_id'] is not None else 'NULL'},
        '{rate['cancellation_reason']}',
        '{rate['is_active']}',
        '{rate['created_at']}',
        '{rate['updated_at']}',
        '{rate['status']}',
        {rate['sign']},
        {rate['version']},
)"""
        values.append(value)
        
    query += ", ".join(values)
    client.command(query)
    
    QuotationFclFreightRateStatistic.delete().execute()

def send_shipment_stats_to_clickhouse(client=get_clickhouse_client):
    query = (
        "INSERT INTO  brahmastra.fcl_freight_rate_statistics SETTINGS async_insert=1, wait_for_async_insert=1 VALUES"
    )

    values = []
    for rate in json_encoder_for_clickhouse(list(ShipmentFclFreightRateStatistic.select().dicts())):
        value = value = f"""(
        {rate['id']},
        '{rate['spot_search_id']}',
        '{rate['spot_search_fcl_customs_services_id']}',
        '{rate['checkout_id']}',
        {f"'{rate['checkout_fcl_freight_rate_services_id']}'" if rate['checkout_fcl_freight_rate_services_id'] is not None else 'NULL'},
        '{rate['sell_quotation_id']}',
        '{rate['buy_quotation_id']}',
        '{rate['validity_id']}',
        '{rate['rate_id']}',
        {f"'{rate['shipment_id']}'" if rate['shipment_id'] is not None else 'NULL'},
        {f"'{rate['shipment_fcl_freight_rate_services_id']}'" if rate['shipment_fcl_freight_rate_services_id'] is not None else 'NULL'},
        '{rate['cancellation_reason']}',
        '{rate['is_active']}',
        '{rate['created_at']}',
        '{rate['updated_at']}',
        '{rate['status']}',
        {rate['sign']},
        {rate['version']}
)"""
        values.append(value)
        
    query += ", ".join(values)
    client.command(query)
    
    ShipmentFclFreightRateStatistic.delete().execute()

def send_spot_search_stats_to_clickhouse(client=get_clickhouse_client):
    query = (
        "INSERT INTO  brahmastra.fcl_freight_rate_statistics SETTINGS async_insert=1, wait_for_async_insert=1 VALUES"
    )

    values = []
    for rate in json_encoder_for_clickhouse(list(SpotSearchFclFreightRateStatistic.select().dicts())):
        value = value = f"""(
        {rate['id']},
        {rate['fcl_freight_rate_statistic_id']},
        '{rate['spot_search_id']}',
        '{rate['spot_search_fcl_freight_services_id']}',
        {f"'{rate['checkout_id']}'" if rate['checkout_id'] is not None else 'NULL'},
        {f"'{rate['checkout_fcl_freight_rate_services_id']}'" if rate['checkout_fcl_freight_rate_services_id'] is not None else 'NULL'},
        {f"'{rate['validity_id']}'" if rate['validity_id'] is not None else 'NULL'},
        {f"'{rate['rate_id']}'" if rate['rate_id'] is not None else 'NULL'},
        {f"'{rate['sell_quotation_id']}'" if rate['sell_quotation_id'] is not None else 'NULL'},
        {f"'{rate['buy_quotation_id']}'" if rate['buy_quotation_id'] is not None else 'NULL'},
        {f"'{rate['shipment_id']}'" if rate['shipment_id'] is not None else 'NULL'},
        '{rate['created_at']}',
        '{rate['updated_at']}',
        {rate['sign']},
        {rate['version']}
)"""
        values.append(value)
        
    query += ", ".join(values)
    client.command(query)
    
    SpotSearchFclFreightRateStatistic.delete().execute()