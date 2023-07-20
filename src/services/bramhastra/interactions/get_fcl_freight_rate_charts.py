
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_connection
from services.bramhastra.clickhouse.connect import get_clickhouse_client

POSSIBLE_DIRECT_FILTERS = [
    'origin_port_id', 'origin_country_id', 'origin_trade_id', 'origin_continent_id', 'destination_port_id', 'destination_country_id', 'destination_trade_id', 'destination_continent_id', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'container_size', 'container_type', 'commodity', 'origin_main_port_id', 'destination_main_port_id', 'procured_by_id','rate_type', 'mode','market_price','sourced_by_id','procured_by_id'
]

def get_fcl_freight_rate_default_stats(include = {'deviation','accuracy'}):
    pass
    