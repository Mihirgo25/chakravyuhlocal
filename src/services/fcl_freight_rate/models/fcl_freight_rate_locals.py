from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from pydantic import BaseModel as pydantic_base_model
import requests

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
    created_at = DateTimeField(default=datetime.datetime.now)
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
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'fcl_freight_rate_locals'
        indexes = (
            (('container_size', 'container_type', 'commodity'), False),
            (('container_type', 'commodity'), False),
            (('port_id', 'container_size', 'container_type', 'commodity', 'trade_type', 'is_line_items_error_messages_present', 'service_provider_id'), False),
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

    def set_location_columns(self):

        obj = {"filters" : {"id": [str(self.port_id)]}}

        port = requests.request("GET", 'https://api-nirvana1.dev.cogoport.io/location/list_locations', json = obj).json()['list'][0]

        self.country_id = port['country_id']
        self.trade_id = port['trade_id'] 
        self.continent_id = port['continent_id']
        self.location_ids = [x for x in [self.port_id, self.country_id, self.trade_id, self.continent_id] if x is not None]

    def before_save(self):
        # data #store model validation

        set_location_columns


idx1 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id == None).where(FclFreightRateLocal.commodity == None)

idx2 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.commodity, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id == None).where(FclFreightRateLocal.commodity != None)

idx3 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.main_port_id, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.commodity, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id != None).where(FclFreightRateLocal.commodity != None)

idx4 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.main_port_id, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id != None).where(FclFreightRateLocal.commodity == None)

FclFreightRateLocal.add_index(idx1)
FclFreightRateLocal.add_index(idx2)
FclFreightRateLocal.add_index(idx3)
FclFreightRateLocal.add_index(idx4)
