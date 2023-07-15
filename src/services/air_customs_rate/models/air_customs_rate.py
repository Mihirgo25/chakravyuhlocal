from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import TRADE_TYPES
from database.rails_db import *
from micro_services.client import common, maps
import datetime
from fastapi import HTTPException
from configs.definitions import AIR_CUSTOMS_CHARGES
from configs.air_customs_rate_constants import COMMODITIES
from services.air_freight_rate.constants.air_freight_rate_constants import RATE_TYPES

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirCustomsRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    airport_id = UUIDField(index=True, null= True)
    country_id = UUIDField(index=True, null= True)
    trade_id = UUIDField(index=True, null=True)
    continent_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    commodity = CharField(null=True, index=True)
    commodity_type = CharField(index=True)
    commodity_sub_type = CharField(index=True)
    service_provider_id = UUIDField(index=True, null = True)
    importer_exporter_id = UUIDField(null=True)
    line_items = BinaryJSONField(null=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    sourced_by_id = UUIDField(null=True, index=True)
    procured_by_id = UUIDField(null=True, index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    service_provider = BinaryJSONField(null=True)
    importer_exporter = BinaryJSONField(null=True)
    airport = BinaryJSONField(null=True)
    mode = CharField(default = 'manual', null = True)
    tags = BinaryJSONField(null=True)
    rate_type = CharField(default='market_place', choices = RATE_TYPES)
    accuracy = FloatField(default = 100, null = True)

    class Meta:
        table_name = 'air_customs_rates'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirCustomsRate, self).save(*args, **kwargs)
    
    def validate_duplicate_line_items(self):
        unique_line_items = set([line_item.get('code').upper() for line_item in self.line_items])
        if len(unique_line_items) != len(self.line_items):
            raise HTTPException(status_code = 400, detail = 'Line Items Contains Duplicates')
        
    def mandatory_charge_codes(self):
        mandatory_charge_codes = []
        for code, config in self.possible_charge_codes().items():
            if 'mandatory' in config.get('tags'):
                mandatory_charge_codes.append(code.upper())
        
        return mandatory_charge_codes
                
    def get_line_items_total_price(self):
        currency = self.line_items[0].get('currency')
        total_price = 0

        for line_item in self.line_items:
            total_price += common.get_money_exchange_for_fcl({'price':line_item.get('price'), 'from_currency':line_item.get('currency'), 'to_currency':currency})['price']
        
        return total_price

    def get_mandatory_line_items(self):
        mandatory_line_items = []
        for line_item in self.line_items:
            if line_item.get('code').upper() in self.mandatory_charge_codes():
                mandatory_line_items.append(line_item)
        
        return mandatory_line_items
    
    def update_line_item_messages(self):
        self.line_items_error_messages = {}
        self.line_items_info_messages = {}
        self.is_line_items_error_messages_present = False
        self.is_line_items_info_messages_present = False

        grouped_charge_codes = {}
        for line_item in self.line_items:
            grouped_charge_codes[line_item.get('code')] = grouped_charge_codes.get(line_item.get('code'),[]) + [line_item]

        for code, line_items in grouped_charge_codes.items():
            code_config = AIR_CUSTOMS_CHARGES.get(code)

            if not code_config:
                self.line_items_error_messages[code] = ['is invalid']
                self.is_line_items_error_messages_present = True
                continue

            if not self.trade_type in code_config.get('trade_types'):
                self.line_items_error_messages[code] = [f"can only be added for {', '.join(code_config['trade_types'])}"]
                self.is_line_items_error_messages_present = True
                continue
            
            line_item_units = [line_item.get('unit') for line_item in line_items]
            if len(list(set(line_item_units).difference(code_config['units']))) > 0:
                self.line_items_error_messages[code] = [f"can only be having units {', '.join(code_config['units'])}"]
                self.is_line_items_error_messages_present = True
                continue
                
            if not eval(str(code_config['condition'] or '')):
                self.line_items_error_messages[code] = ['is invalid']
                self.is_line_items_error_messages_present = True
                continue

        for code, config in self.possible_charge_codes().items():
            if 'mandatory' in config.get('tags'):
                if not grouped_charge_codes.get(code):
                    self.line_items_error_messages[code] = ['is not present']
                    self.is_line_items_error_messages_present = True
            
            if 'additional_service' in config.get('tags') or 'shipment_execution_service' in config.get('tags'):
                if not grouped_charge_codes.get(code):
                    self.line_items_info_messages[code] = ['can be added for more conversion']
                    self.is_line_items_info_messages_present = True
        
        self.save()


    def detail(self):
        return {
            'air_customs':{
            'line_items':self.line_items,
            'line_items_info_messages':self.line_items_info_messages,
            'is_line_items_info_messages_present':self.is_line_items_info_messages_present,
            'line_items_error_messages':self.line_items_error_messages,
            'is_line_items_error_messages_present':self.is_line_items_error_messages_present,
            }
        }
    
    def possible_charge_codes(self):
        self.set_airport()
        air_custom_charges = AIR_CUSTOMS_CHARGES
        airport = self.airport
        
        charge_codes = {}
        for code, config in air_custom_charges.items():
            if config.get('condition') is not None and eval(str(config['condition'])) and self.trade_type in config.get('trade_types'):
                charge_codes[code] = config
        return charge_codes

    def set_airport(self):
        if self.airport or (not self.airport_id):
            return
        
        required_params = {
            "id": True,
            "name": True,
            "display_name": True,
            "port_code": True,
            "country_id": True,
            "continent_id": True,
            "trade_id": True,
            "country_code": True,
            "type":True
        }
        
        airport_data = maps.list_locations({'filters':{'id': self.airport_id},'includes':required_params})['list']
        if airport_data:
            self.airport = airport_data[0]
        else:
            self.airport = {}

    def set_location_ids(self):
        self.country_id = self.airport.get('country_id')
        self.trade_id = self.airport.get('trade_id')
        self.continent_id = self.airport.get('continent_id')
        self.location_ids = list(filter(None, [uuid.UUID(self.airport_id),uuid.UUID(self.country_id),uuid.UUID(self.trade_id),uuid.UUID(self.continent_id)]))

    def validate_service_provider_id(self):
        if not self.service_provider_id:
            return
        service_provider_data = get_organization(id=self.service_provider_id)
        if len(service_provider_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid service provider ID")
        
    def validate_trade_type(self):
        if self.trade_type and self.trade_type not in TRADE_TYPES:
            raise HTTPException(status_code = 400, detail = 'Invalid Trade Type')
        
    def validate_commodity(self):
        if self.commodity not in COMMODITIES:
            raise HTTPException(status_code = 400, detail = 'Invalid Commodity')
    
    def validate_rate_type(self):
        if self.rate_type not in RATE_TYPES:
            raise HTTPException(status_code = 400, detail = 'Invalid Rate Type')

    def validate_uniqueness(self):
        uniqueness = AirCustomsRate.select(AirCustomsRate.id).where(
            AirCustomsRate.airport_id == self.airport_id,
            AirCustomsRate.trade_type == self.trade_type,
            AirCustomsRate.commodity == self.commodity,
            AirCustomsRate.service_provider_id == self.service_provider_id,
            AirCustomsRate.importer_exporter_id == self.importer_exporter_id
        ).count()

        if self.id and uniqueness == 1:
            return True
        if not self.id and uniqueness == 0:
            return True
        return False

    def validate_before_save(self):
        self.validate_duplicate_line_items()
        self.validate_service_provider_id()
        self.validate_trade_type()
        self.validate_commodity()
        self.validate_rate_type()
        self.validate_uniqueness()