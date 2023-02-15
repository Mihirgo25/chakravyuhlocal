from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from pydantic import BaseModel as pydantic_base_model
import requests
from configs.fcl_freight_rate_constants import TRADE_TYPES, CONTAINER_SIZES, CONTAINER_TYPES, LOCAL_CONTAINER_COMMODITY_MAPPINGS
from fastapi import HTTPException

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
    port: dict = None
    shipping_line: dict = None

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

        self.port = requests.request("GET", 'https://api-nirvana1.dev.cogoport.io/location/list_locations', json = obj).json()['list'][0]

        self.country_id = self.port['country_id']
        self.trade_id = self.port['trade_id'] 
        self.continent_id = self.port['continent_id']
        self.location_ids = [x for x in [self.port_id, self.country_id, self.trade_id, self.continent_id] if x is not None]

    def set_shipping_line(self):
      self.shipping_line = requests.get("https://api-nirvana1.dev.cogoport.io/operator/list_operators?filters%5Bid%5D[]=" + str(self.shipping_line_id)).json()['list'][0]

    def validate_main_port_id(self):
        if self.port and self.port['is_icd']==False:
            if self.main_port_id:
                return False
        
        #some validation

        return True

    def validate_shipping_line_id(self):
        return True

    def validate_service_provider_id(self):
        return True

    def validate_trade_type(self):
        if self.trade_type not in TRADE_TYPES:
            return False
        
        return True

    def validate_container_size(self):
        if self.container_size not in CONTAINER_SIZES:
            return False
        
        return True

    def validate_container_type(self):
        if self.container_type not in CONTAINER_TYPES:
            return False
        
        return True


    def validate_uniqueness(self):
      freight_local_cnt = FclFreightRateLocal.select().where(
        FclFreightRateLocal.port_id == self.port_id,
        FclFreightRateLocal.trade_type == self.trade_type,
        FclFreightRateLocal.main_port_id == self.main_port_id,
        FclFreightRateLocal.container_size == self.container_size,
        FclFreightRateLocal.container_type == self.container_type,
        FclFreightRateLocal.commodity == self.commodity,
        FclFreightRateLocal.shipping_line_id == self.shipping_line_id,
        FclFreightRateLocal.service_provider_id == self.service_provider_id
      ).count()

      if self.id and freight_local_cnt==1:
        return True
      if not self.id and freight_local_cnt==0:
        return True

      return False

    def validate_commodity(self):
        if self.container_type and self.commodity not in LOCAL_CONTAINER_COMMODITY_MAPPINGS:
            return False
        
        return True

    def before_save(self):
        # data #store model validation

        if not self.validate_main_port_id:
            HTTPException(status_code=499, detail='main_port_id is not valid')

        if not self.validate_shipping_line_id:
            HTTPException(status_code=499, detail='shipping_line_id is not valid')

        if not self.validate_service_provider_id:
            HTTPException(status_code=499, detail='service_provider_id is not valid')
        
        if not self.validate_trade_type:
            HTTPException(status_code=499, detail='trade_type is not valid')

        if not self.validate_container_size:
            HTTPException(status_code=499, detail='container_size is not valid')
        
        if not self.validate_container_type:
            HTTPException(status_code=499, detail='container_type is not valid')

        if not self.validate_uniqueness:
            HTTPException(status_code=499, detail='violates uniqueness validation')

    def local_data_get_line_item_messages(self):

      location_ids = list(set([item.location_id for item in self.origin_local.line_items if item.location_id is not None]))

      locations = {}

      if location_ids:
        obj = {"filters" : {"id": location_ids}}
        locations = requests.request("GET", 'https://api-nirvana1.dev.cogoport.io/location/list_locations', json = obj).json()['list']

      return locations

    def update_line_item_messages(self):
      response = {}

      if self.origin_local:
        response = self.local_data_get_line_item_messages()

      self.update(
        line_items_error_messages = response['line_items_error_messages'],
        is_line_items_error_messages_present = response['is_line_items_error_messages_present'],
        line_items_info_messages = response['line_items_info_messages'],
        is_line_items_info_messages_present = response['is_line_items_info_messages_present']
      )

    def update_free_days_special_attributes(self):
      self.update(
        is_detention_slabs_missing = (len(self.data['detention']['slabs']) == 0),
        is_demurrage_slabs_missing = (len(self.data['demurrage']['slabs']) == 0),
        is_plugin_slabs_missing = (len(self.data['plugin']['slabs']) == 0)
      )

    def update_special_attributes(self):
        self.update_line_item_messages
        self.update_free_days_special_attributes
    

        


idx1 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id == None).where(FclFreightRateLocal.commodity == None)

idx2 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.commodity, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id == None).where(FclFreightRateLocal.commodity != None)

idx3 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.main_port_id, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.commodity, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id != None).where(FclFreightRateLocal.commodity != None)

idx4 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.main_port_id, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id != None).where(FclFreightRateLocal.commodity == None)

FclFreightRateLocal.add_index(idx1)
FclFreightRateLocal.add_index(idx2)
FclFreightRateLocal.add_index(idx3)
FclFreightRateLocal.add_index(idx4)
