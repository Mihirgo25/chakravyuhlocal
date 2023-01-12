from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        
class FclFreightRate(BaseModel):
    commodity = CharField(null=True)
    container_size = CharField(null=True)
    container_type = CharField(null=True)
    containers_count = IntegerField(null=True)
    created_at = DateTimeField()
    destination_continent_id = UUIDField(index=True, null=True)
    destination_country_id = UUIDField(index=True, null=True)
    destination_demurrage_id = UUIDField(index=True, null=True)
    destination_detention_id = UUIDField(index=True, null=True)
    destination_local = BinaryJSONField(null=True)
    destination_local_id = UUIDField(index=True, null=True)
    destination_local_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    destination_local_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    destination_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    destination_main_port_id = UUIDField(null=True)
    destination_plugin_id = UUIDField(index=True, null=True)
    destination_port_id = UUIDField(index=True, null=True)
    destination_trade_id = UUIDField(index=True, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(null=True)
    importer_exporters_count = IntegerField(null=True)
    is_best_price = BooleanField(null=True)
    is_destination_demurrage_slabs_missing = BooleanField(index=True, null=True)
    is_destination_detention_slabs_missing = BooleanField(index=True, null=True)
    is_destination_local_line_items_error_messages_present = BooleanField(index=True, null=True)
    is_destination_local_line_items_info_messages_present = BooleanField(index=True, null=True)
    is_destination_plugin_slabs_missing = BooleanField(index=True, null=True)
    is_origin_demurrage_slabs_missing = BooleanField(index=True, null=True)
    is_origin_detention_slabs_missing = BooleanField(index=True, null=True)
    is_origin_local_line_items_error_messages_present = BooleanField(index=True, null=True)
    is_origin_local_line_items_info_messages_present = BooleanField(index=True, null=True)
    is_origin_plugin_slabs_missing = BooleanField(index=True, null=True)
    is_weight_limit_slabs_missing = BooleanField(null=True)
    last_rate_available_date = DateField(null=True)
    omp_dmp_sl_sp = CharField(null=True)
    origin_continent_id = UUIDField(index=True, null=True)
    origin_country_id = UUIDField(index=True, null=True)
    origin_detention_id = UUIDField(index=True, null=True)
    origin_local = BinaryJSONField(null=True)
    origin_local_id = UUIDField(index=True, null=True)
    origin_local_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    origin_local_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    origin_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    origin_main_port_id = UUIDField(null=True)
    origin_plugin_id = UUIDField(index=True, null=True)
    origin_port_id = UUIDField(null=True)
    origin_trade_id = UUIDField(index=True, null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    service_provider_id = UUIDField(index=True, null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    updated_at = DateTimeField()
    validities = BinaryJSONField(null=True)
    weight_limit = BinaryJSONField(null=True)
    weight_limit_id = UUIDField(index=True, null=True)

    class Meta:
        table_name = 'fcl_freight_rates'
        indexes = (
            (('container_size', 'container_type', 'commodity'), False),
            (('container_type', 'commodity'), False),
            (('importer_exporter_id', 'service_provider_id'), False),
            (('origin_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'importer_exporter_id', 'rate_not_available_entry', 'last_rate_available_date', 'omp_dmp_sl_sp'), False),
            (('origin_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('origin_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id'), True),
            (('priority_score', 'id', 'service_provider_id'), False),
            (('priority_score', 'service_provider_id'), False),
            (('priority_score', 'service_provider_id', 'importer_exporter_id'), False),
            (('priority_score', 'service_provider_id', 'is_best_price'), False),
            (('priority_score', 'service_provider_id', 'last_rate_available_date'), False),
            (('priority_score', 'service_provider_id', 'rate_not_available_entry'), False),
            (('priority_score', 'service_provider_id', 'shipping_line_id', 'is_best_price'), False),
            (('priority_score', 'service_provider_id', 'shipping_line_id', 'rate_not_available_entry'), False),
            (('service_provider_id', 'id'), False),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'commodity'), False),
            (('updated_at', 'id', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id'), False),
        )
    
    