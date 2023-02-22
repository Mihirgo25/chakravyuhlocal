from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
from rails_client import client
import datetime
from pydantic import BaseModel as pydantic_base_model
import requests
from configs.fcl_freight_rate_constants import TRADE_TYPES, CONTAINER_SIZES, CONTAINER_TYPES, LOCAL_CONTAINER_COMMODITY_MAPPINGS,HAZ_CLASSES
from fastapi import HTTPException
import yaml
from configs.defintions import FCL_FREIGHT_LOCAL_CHARGES
from services.fcl_freight_rate.models.fcl_freight_rate_local_data import FclFreightRateLocalData


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
    # data = FclFreightRateLocalData(null=True)
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

    def validate_port(self):
        obj = {"filters" : {"id": [str(self.port_id)]}}
        port_data = client.ruby.list_locations(obj)['list'][0]
        if port_data.get('type') == 'seaport':
            self.port = port_data

            self.country_id = self.port['country_id']
            self.trade_id = self.port['trade_id'] 
            self.continent_id = self.port['continent_id']
            self.location_ids = [uuid.UUID(str(x)) for x in [self.port_id, self.country_id, self.trade_id, self.continent_id] if x is not None]
            print()
            return True
        return False

    def validate_main_port_id(self):
        self.main_port=None
        if self.port and self.port['is_icd']==False:
            if self.main_port_id:
                return False
        elif self.port and self.port['is_icd']==True:
            if self.main_port_id:
                main_port_data = client.ruby.list_locations({"filters" : {"id": [str(self.main_port_id)]}})['list'][0]
                if main_port_data['type'] == 'seaport' and main_port_data['is_icd'] == False:
                    self.main_port = main_port_data
                    return True
                return False
            else:
                return False
        return True

    def validate_shipping_line_id(self):
        shipping_line_data = client.ruby.list_operators({'filters':{'id': [str(self.shipping_line_id)]}})['list'][0]
        if shipping_line_data.get('operator_type') == 'shipping_line':#Can we check like this as we are getting through id so we will get only single row or should we send it as a param filter
            self.shipping_line = shipping_line_data
            return True
        return False

    def validate_service_provider_id(self):
        service_provider_data = client.ruby.list_organizations({'filters':{'id': [str(self.service_provider_id)]}})['list'][0]
        if service_provider_data.get('account_type') == 'service_provider':
            self.service_provider = service_provider_data
            return True
        return False

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
    
    def validate_commodity(self):
        if self.container_type and self.commodity not in LOCAL_CONTAINER_COMMODITY_MAPPINGS:
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
    #   if not self.id and freight_local_cnt==0:
    #     return True

      return False
    
    def validate_data(self):
        self.local_data_instance.validate_duplicate_charge_codes()# for each part different error should occur
        print("ababab")
        print('ahgsdjhagshjsgdadajsdgjhagdqgeiygdiquwgdiuqwgdiuqwgdiquwgdiuqgwdiuqwgdiyfgqwiuydfgq',self.local_data_instance,'hiuasdghuiasgh', type(self.local_data_instance))
        self.local_data_instance.validate_invalid_charge_codes(self.possible_charge_codes())

    def before_save(self):
        # data #store model validation
        try:
            self.local_data_instance = FclFreightRateLocalData(self.data)
            t = FclFreightRateLocalData(self.data)
            print("bedada",t)
            print("line_items",self.local_data_instance.line_items)
        except Exception as e:
            print("=========",e)

        if not self.validate_port():
            HTTPException(status_code=499, detail='port_id is not valid')

        if not self.validate_main_port_id():
            HTTPException(status_code=499, detail='main_port_id is not valid')

        if not self.validate_shipping_line_id():
            HTTPException(status_code=499, detail='shipping_line_id is not valid')

        if not self.validate_service_provider_id():
            HTTPException(status_code=499, detail='service_provider_id is not valid')
        
        if not self.validate_trade_type():
            HTTPException(status_code=499, detail='trade_type is not valid')

        if not self.validate_container_size():
            HTTPException(status_code=499, detail='container_size is not valid')
        
        if not self.validate_container_type():
            HTTPException(status_code=499, detail='container_type is not valid')

        if not self.validate_uniqueness():
            HTTPException(status_code=499, detail='violates uniqueness validation')

        if not self.validate_data():
            HTTPException(status_code=499, detail='data is not valid')

    # def local_data_get_line_item_messages(self):

    #   location_ids = list(set([item.location_id for item in self.origin_local.line_items if item.location_id is not None]))

    #   locations = {}

    #   if location_ids:
    #     obj = {"filters" : {"id": location_ids}}
    #     locations = requests.request("GET", 'https://api-nirvana1.dev.cogoport.io/location/list_locations', json = obj).json()['list']

    #   return locations

    def update_special_attributes(self):
        self.update_line_item_messages()
        self.update_free_days_special_attributes()

    def update_line_item_messages(self):
        self.set_port()
        self.set_shipping_line()
        response = {}

        try:
            response = self.local_data_instance.get_line_item_messages(self.port, self.main_port, self.shipping_line, self.container_size, self.container_type, self.commodity,self.trade_type,self.possible_charge_codes())
        except Exception as e:
            print(e)
        print('hua', response)
        
        self.update(
            line_items_error_messages = response['line_items_error_messages'],
            is_line_items_error_messages_present = response['is_line_items_error_messages_present'],
            line_items_info_messages = response['line_items_info_messages'],
            is_line_items_info_messages_present = response['is_line_items_info_messages_present']
        )

    def update_free_days_special_attributes(self):
        try:
            self.update(
                is_detention_slabs_missing = (len(self.data['detention']['slabs']) == 0),
                is_demurrage_slabs_missing = (len(self.data['demurrage']['slabs']) == 0),
                is_plugin_slabs_missing = (len(self.data['plugin']['slabs']) == 0)
            )
        except Exception as e:
            print(e)

    def set_port(self):
        if self.port:
            return
        
        if not self.port_id:
            return
        
        location_ids = [str(self.port_id)]
        if self.main_port_id:
            location_ids.append(str(self.main_port_id))
        ports = client.ruby.list_locations({'filters': {'id': location_ids}, 'pagination_data_required': False})['list']
        for port in ports:
            if port.get('id') == self.port_id:
                self.port = port
            elif self.main_port_id and port.get('id') == self.main_port_id:
                self.main_port = port

    def set_shipping_line(self):
        if self.shipping_line or not self.shipping_line_id:
            return
        self.shipping_line = client.ruby.list_operators({'filters': { id: self.shipping_line_id }, 'pagination_data_required': False})['list'][0]

    def possible_charge_codes(self):
        self.set_port()
        print(self.port)
        self.set_shipping_line()
        print("igf")
        
        # setting variables for conditions in charges.yml
        port = self.port
        main_port = self.main_port
        shipping_line = self.shipping_line
        container_size = self.container_size
        container_type = self.container_type
        commodity = self.commodity
        
        with open(FCL_FREIGHT_LOCAL_CHARGES, 'r') as file:
            try:
                fcl_freight_local_charges_dict = yaml.safe_load(file)
            except Exception as e:
                print(e)

        try:
            charge_codes = {}
            for code, config in fcl_freight_local_charges_dict.items():
                if config.get('condition') is not None and eval(str(config['condition'])) and self.trade_type in config['trade_types']:
                    charge_codes[code] = config

            # charge_codes = {
            #     code: config for code, config in fcl_freight_local_charges_dict.items()
            #     if config.get('condition') is not None and
            #     eval(str(config['condition'])) and self.trade_type in config['trade_types']
            # }
        except Exception as e:
            print(e)
        return charge_codes

    def update_freight_objects(self):
        try:
            from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
            location_key = 'origin' if self.trade_type == 'export' else 'destination'
            print("bedada")
            t = FclFreightRate.get_or_none(
            FclFreightRate.container_size == self.container_size,
            FclFreightRate.container_type == self.container_type,
            FclFreightRate.shipping_line_id == self.shipping_line_id,
            FclFreightRate.service_provider_id == self.service_provider_id,
            eval(f"FclFreightRate.{location_key}_port_id") == self.port_id,
            eval(f"FclFreightRate.{location_key}_main_port_id") == self.main_port_id
            )

            if t:
                print('kay')
                if self.commodity:
                    t = t.where(FclFreightRate.commodity == self.commodity)

                t=t.where(f"FclFreightRate.{location_key}_local_id" == None)
                print('aiosjdhas',t)
                setattr(t, f"{location_key}_local_id", self.id)
                # t.update({f"FclFreightRate.{location_key}_local_id": self.id}).execute()
                

            print(t)
        except Exception as e:
            print(e)
        #not working



idx1 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id == None).where(FclFreightRateLocal.commodity == None)

idx2 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.commodity, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id == None).where(FclFreightRateLocal.commodity != None)

idx3 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.main_port_id, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.commodity, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id != None).where(FclFreightRateLocal.commodity != None)

idx4 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.main_port_id, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id != None).where(FclFreightRateLocal.commodity == None)

FclFreightRateLocal.add_index(idx1)
FclFreightRateLocal.add_index(idx2)
FclFreightRateLocal.add_index(idx3)
FclFreightRateLocal.add_index(idx4)
