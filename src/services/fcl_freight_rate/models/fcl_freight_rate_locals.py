from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateLocal(BaseModel):
    commodity = CharField(null=True)
    container_size = CharField(null=True)
    container_type = CharField(null=True)
    containers_count = IntegerField(null=True)
    continent_id = UUIDField(index=True, null=True)
    country_id = UUIDField(index=True, null=True)
    created_at = DateTimeField()
    data = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    demurrage_id = UUIDField(index=True, null=True)
    detention_id = UUIDField(index=True, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporters_count = IntegerField(null=True)
    is_demurrage_slabs_missing = BooleanField(index=True, null=True)
    is_detention_slabs_missing = BooleanField(index=True, null=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    is_plugin_slabs_missing = BooleanField(index=True, null=True)
    line_items = BinaryJSONField(null=True)
    line_items_error_messages = BinaryJSONField(null=True)
    line_items_info_messages = BinaryJSONField(null=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    main_port_id = UUIDField(null=True)
    plugin_id = UUIDField(index=True, null=True)
    port_id = UUIDField(index=True, null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    rate_not_available_entry = BooleanField(null=True)
    selected_suggested_rate_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    trade_id = UUIDField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'fcl_freight_rate_locals'
        indexes = (
            (('container_size', 'container_type', 'commodity'), False),
            (('container_type', 'commodity'), False),
            (('port_id', 'container_size', 'container_type', 'commodity', 'trade_type', 'is_line_items_error_messages_present', 'service_provider_id'), False),
            (('port_id', 'trade_type', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('port_id', 'trade_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id'), True),
            (('port_id', 'trade_type', 'main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id'), True),
            (('port_id', 'trade_type', 'main_port_id', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id'), True),
            (('priority_score', 'id', 'service_provider_id'), False),
            (('priority_score', 'service_provider_id'), False),
            (('priority_score', 'service_provider_id', 'is_line_items_error_messages_present'), False),
            (('priority_score', 'service_provider_id', 'is_line_items_info_messages_present'), False),
            (('priority_score', 'service_provider_id', 'port_id'), False),
            (('priority_score', 'service_provider_id', 'shipping_line_id', 'is_line_items_error_messages_present'), False),
            (('priority_score', 'service_provider_id', 'shipping_line_id', 'is_line_items_info_messages_present'), False),
            (('priority_score', 'service_provider_id', 'trade_type', 'is_line_items_error_messages_present'), False),
            (('priority_score', 'service_provider_id', 'trade_type', 'is_line_items_info_messages_present'), False),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'port_id'), False),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'trade_type'), False),
            (('updated_at', 'id', 'service_provider_id'), False),
            (('updated_at', 'id', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id'), False),
        )