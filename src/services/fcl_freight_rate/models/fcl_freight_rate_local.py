from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
from rails_client import client
import datetime
from configs.fcl_freight_rate_constants import TRADE_TYPES, CONTAINER_SIZES, CONTAINER_TYPES, LOCAL_CONTAINER_COMMODITY_MAPPINGS,HAZ_CLASSES
from fastapi import HTTPException
import yaml
from configs.defintions import FCL_FREIGHT_LOCAL_CHARGES
from services.fcl_freight_rate.models.fcl_freight_rate_local_data import FclFreightRateLocalData
from libs.locations import list_locations


class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateLocal(BaseModel):
    commodity = CharField(null=True)
    container_size = CharField(index=True, null=True)
    container_type = CharField(index=True, null=True)
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
    is_local_agent_rate = BinaryJSONField(null=True)
    is_plugin_slabs_missing = BooleanField(index=True, null=True)
    line_items = BinaryJSONField(null=True)
    line_items_error_messages = BinaryJSONField(null=True)
    line_items_info_messages = BinaryJSONField(null=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    main_port_id = UUIDField(null=True)
    main_port = BinaryJSONField(null=True)
    plugin_id = UUIDField(index=True, null=True)
    port_id = UUIDField(index=True, null=True)
    port = BinaryJSONField(null=True)
    priority_score = IntegerField(null=True)
    priority_score_updated_at = DateTimeField(null=True)
    procured_by_id = UUIDField(null=True)
    procured_by = BinaryJSONField(null=True)
    rate_not_available_entry = BooleanField(null=True)
    selected_suggested_rate_id = UUIDField(null=True)
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    shipping_line = BinaryJSONField(null=True)
    sourced_by_id = UUIDField(null=True)
    sourced_by = BinaryJSONField(null=True)
    trade_id = UUIDField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateLocal, self).save(*args, **kwargs)


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
        obj = {"id": [str(self.port_id)]}
        port_data = list_locations(obj)['list']
        if len(port_data) != 0 and port_data[0].get('type') == 'seaport':
            self.port = port_data[0]

            self.country_id = port_data[0].get('country_id', None)
            self.trade_id = port_data[0].get('trade_id', None) 
            self.continent_id = port_data[0].get('continent_id', None)
            self.location_ids = [uuid.UUID(str(x)) for x in [self.port_id, self.country_id, self.trade_id, self.continent_id] if x is not None]

            return True
        return False

    def validate_main_port_id(self):
        self.main_port=None
        if self.port and self.port['is_icd']==False:
            if not self.main_port_id or self.main_port_id != self.port_id:
                return True
            return False
        elif self.port and self.port['is_icd']==True:
            if self.main_port_id:
                main_port_data = list_locations({'id': [str(self.main_port_id)]})['list']
                if len(main_port_data) != 0 and main_port_data[0].get('type') == 'seaport' and main_port_data[0].get('is_icd') == False:
                    self.main_port = main_port_data[0]
                    return True
                return False
            else:
                return False
        return True

    def validate_shipping_line_id(self):
        shipping_line_data = client.ruby.list_operators({'filters':{'id': [str(self.shipping_line_id)]}})['list']
        if len(shipping_line_data) != 0 and shipping_line_data[0].get('operator_type') == 'shipping_line':
            self.shipping_line = shipping_line_data[0]
            return True
        return False

    def validate_service_provider_id(self):
        service_provider_data = client.ruby.list_organizations({'filters':{'id': [str(self.service_provider_id)]}})['list']
        if len(service_provider_data) != 0 and service_provider_data[0].get('account_type') == 'service_provider':
            self.service_provider = service_provider_data[0]
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
      if not self.id and freight_local_cnt==0:
        return True

      return False
    
    def validate_data(self):
        return self.local_data_instance.validate_duplicate_charge_codes() and self.local_data_instance.validate_invalid_charge_codes(self.possible_charge_codes())

    def validate_before_save(self):
        self.local_data_instance = FclFreightRateLocalData(self.data)

        if not self.validate_port():
            raise HTTPException(status_code=499, detail='port_id is not valid')

        if not self.validate_main_port_id():
            raise HTTPException(status_code=499, detail='main_port_id is not valid')

        if not self.validate_shipping_line_id():
            raise HTTPException(status_code=499, detail='shipping_line_id is not valid')

        if not self.validate_service_provider_id():
            raise HTTPException(status_code=499, detail='service_provider_id is not valid')
        
        if not self.validate_trade_type():
            raise HTTPException(status_code=499, detail='trade_type is not valid')

        if not self.validate_container_size():
            raise HTTPException(status_code=499, detail='container_size is not valid')
        
        if not self.validate_container_type():
            raise HTTPException(status_code=499, detail='container_type is not valid')

        if not self.validate_uniqueness():
            raise HTTPException(status_code=499, detail='violates uniqueness validation')

        if not self.validate_data():
            raise HTTPException(status_code=499, detail='data is not valid')

    def update_special_attributes(self):
        self.update_line_item_messages()
        self.update_free_days_special_attributes()

    def update_line_item_messages(self):
        self.set_port()
        self.set_shipping_line()
        response = {}

        response = self.local_data_instance.get_line_item_messages(self.port, self.main_port, self.shipping_line_id, self.container_size, self.container_type, self.commodity,self.trade_type,self.possible_charge_codes())

        self.line_items_error_messages = response['line_items_error_messages'],
        self.is_line_items_error_messages_present = response['is_line_items_error_messages_present'],
        self.line_items_info_messages = response['line_items_info_messages'],
        self.is_line_items_info_messages_present = response['is_line_items_info_messages_present']

    def update_free_days_special_attributes(self):
        self.is_detention_slabs_missing = len(self.data['detention']['slabs']) == 0 if self.data and self.data.get('detention') else True
        self.is_demurrage_slabs_missing = len(self.data['demurrage']['slabs']) == 0 if self.data and self.data.get('demurrage') else True
        self.is_plugin_slabs_missing = len(self.data['plugin']['slabs']) == 0 if self.data and self.data.get('plugin') else True

    def set_port(self):
        if self.port:
            return
        
        if not self.port_id:
            return
        
        location_ids = [str(self.port_id)]
        if self.main_port_id:
            location_ids.append(str(self.main_port_id))
        ports = list_locations({'id': location_ids})['list']
        for port in ports:
            if port.get('id') == self.port_id:
                self.port = port
            elif self.main_port_id and port.get('id') == self.main_port_id:
                self.main_port = port


    def set_shipping_line(self):
        if self.shipping_line or not self.shipping_line_id:
            return
        shipping_line = client.ruby.list_operators({'filters': { 'id': str(self.shipping_line_id) }, 'pagination_data_required': False})['list']
        if len(shipping_line) != 0:
            self.shipping_line = shipping_line[0]

    def possible_charge_codes(self):
        self.set_port()
        self.set_shipping_line()
        
        # setting variables for conditions in charges.yml
        port = self.port
        main_port = self.main_port
        shipping_line_id = self.shipping_line_id
        container_size = self.container_size
        container_type = self.container_type
        commodity = self.commodity

        with open(FCL_FREIGHT_LOCAL_CHARGES, 'r') as file:
            fcl_freight_local_charges_dict = yaml.safe_load(file)

        charge_codes = {}
        for code, config in fcl_freight_local_charges_dict.items():
            if config.get('condition') is not None and eval(str(config['condition'])) and self.trade_type in config['trade_types']:
                charge_codes[code] = config

        return charge_codes

    def update_freight_objects(self):
        from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
        location_key = 'origin' if self.trade_type == 'export' else 'destination'
        if location_key == 'origin':
            kwargs = {
                'origin_local_id':self.id
            }
        else:
            kwargs = {
                'destination_local_id':self.id
            }

        t=FclFreightRate.update(**kwargs).where(
            FclFreightRate.container_size == self.container_size,
            FclFreightRate.container_type == self.container_type,
            FclFreightRate.shipping_line_id == self.shipping_line_id,
            FclFreightRate.service_provider_id == self.service_provider_id,
            (eval("FclFreightRate.{}_port_id".format(location_key)) == self.port_id),
            (eval("FclFreightRate.{}_main_port_id".format(location_key)) == self.main_port_id),
            (FclFreightRate.commodity == self.commodity) if self.commodity else (FclFreightRate.id.is_null(False)),
            (eval("FclFreightRate.{}_local_id".format(location_key)) == None)
            )
        t.execute()

    def detail(self):
        with open(FCL_FREIGHT_LOCAL_CHARGES, 'r') as file:
            fcl_freight_local_charges_dict = yaml.safe_load(file)

        from services.fcl_freight_rate.interaction.list_fcl_freight_rate_free_days import list_fcl_freight_rate_free_days

        if self.detention_id or self.demurrage_id:
            free_days = list_fcl_freight_rate_free_days({'filters': {'id': [str(self.detention_id), str(self.demurrage_id)]}})['list']

        if self.detention_id:
            t = next((t for t in free_days if t['id'] == self.detention_id), None)
            if t:
                self.data['detention'] = {'free_limit':t['free_limit'], 'slabs':t['slabs'], 'remarks':t['remarks']}

        if self.demurrage_id:
            t = next((t for t in free_days if t['id'] == self.demurrage_id), None)
            if t:
                self.data['demurrage'] = {'free_limit':t['free_limit'], 'slabs':t['slabs'], 'remarks':t['remarks']}

        detail = self.data | {
            'id': self.id,
            'line_items_error_messages': self.line_items_error_messages,
            'is_line_items_error_messages_present': self.is_line_items_error_messages_present,
            'line_items_info_messages': self.line_items_info_messages,
            'is_line_items_info_messages_present': self.is_line_items_info_messages_present,
            'is_detention_slabs_missing': self.is_detention_slabs_missing,
            'is_demurrage_slabs_missing': self.is_demurrage_slabs_missing,
            'is_plugin_slabs_missing': self.is_plugin_slabs_missing
        }

        for item in detail['line_items']:
            line_item_name = fcl_freight_local_charges_dict[item['code']]['name'] if item['code'] in fcl_freight_local_charges_dict else item['code']
            item.update({'name': line_item_name})

        return detail


idx1 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id == None).where(FclFreightRateLocal.commodity == None)

idx2 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.commodity, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id == None).where(FclFreightRateLocal.commodity != None)

idx3 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.main_port_id, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.commodity, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id != None).where(FclFreightRateLocal.commodity != None)

idx4 = FclFreightRateLocal.index(FclFreightRateLocal.port_id, FclFreightRateLocal.trade_type, FclFreightRateLocal.main_port_id, FclFreightRateLocal.container_size, FclFreightRateLocal.container_type, FclFreightRateLocal.shipping_line_id, FclFreightRateLocal.service_provider_id, unique=True).where(FclFreightRateLocal.main_port_id != None).where(FclFreightRateLocal.commodity == None)

FclFreightRateLocal.add_index(idx1)
FclFreightRateLocal.add_index(idx2)
FclFreightRateLocal.add_index(idx3)
FclFreightRateLocal.add_index(idx4)
