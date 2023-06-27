from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime, uuid
from micro_services.client import maps, common
from configs.fcl_freight_rate_constants import *
from configs.fcl_customs_rate_constants import CONTAINER_TYPE_COMMODITY_MAPPINGS
from database.rails_db import *
from fastapi import HTTPException
from configs.definitions import FCL_CUSTOMS_CHARGES
import uuid

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCustomsRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    location_id = UUIDField(index=True)
    country_id = UUIDField(index=True)
    trade_id = UUIDField(index=True)
    continent_id = UUIDField(index=True)
    trade_type = CharField(null=True)
    container_size = CharField(null=True, index=True)
    container_type = CharField(null=True, index=True)
    commodity = CharField(null=True, index=True)
    service_provider_id = UUIDField(index=True)
    importer_exporter_id = UUIDField(null=True)
    containers_count = IntegerField(null=True)
    customs_line_items = BinaryJSONField(null=True)
    cfs_line_items = BinaryJSONField(null=True)
    platform_price = IntegerField(null=True)
    is_best_price = BooleanField(null=True)
    is_customs_line_items_error_messages_present = BooleanField(null=True)
    is_customs_line_items_info_messages_present = BooleanField(null=True)
    customs_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    customs_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    is_cfs_line_items_error_messages_present = BooleanField(null=True)
    is_cfs_line_items_info_messages_present = BooleanField(null=True)
    cfs_line_items_error_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    cfs_line_items_info_messages = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    location_type = CharField(index=True, null=True)
    sourced_by_id = UUIDField(null=True, index=True)
    procured_by_id = UUIDField(null=True, index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    service_provider = BinaryJSONField(null=True)
    location = BinaryJSONField(null=True)
    importer_exporter = BinaryJSONField(null=True)
    zone_id = UUIDField(index=True,null=True)
    mode = CharField(default = 'manual', null = True)
    tags = BinaryJSONField(null=True)
    rate_type = CharField(default='market_place', choices = RATE_TYPES)
    accuracy = FloatField(default = 100, null = True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCustomsRate, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_customs_rates'

    def set_location_ids(self):
        self.country_id = self.location.get('country_id') 
        self.trade_id = self.location.get('trade_id') 
        self.continent_id = self.location.get('continent_id') 
        self.location_ids = list(filter(None, [uuid.UUID(self.country_id),uuid.UUID(self.trade_id),uuid.UUID(self.continent_id)]))
        
    def set_location_type(self):
        self.location_type = self.location.get('type')
        self.zone_id = self.location.get('zone_id')
 
    def get_line_items_total_price(self):
      line_items = self.customs_line_items
      currency = self.customs_line_items[0].get('currency')
      total_price = 0
      for line_item in line_items:
        total_price += common.get_money_exchange_for_fcl({"price": line_item.get('price'), "from_currency": line_item.get('currency'), "to_currency": currency })['price']
      return total_price

    def set_location(self):
        if self.location or (not self.location_id):
            return
        
        required_params = {
            "id": True,
            "name": True,
            "is_icd": True,
            "port_code": True,
            "country_id": True,
            "continent_id": True,
            "trade_id": True,
            "country_code": True,
            "zone_id":True,
            "type":True
        }
        
        location = maps.list_locations({'filters':{'id': self.location_id},'includes':required_params})['list']
        if location:
            self.location = location[0]
        else:
            self.location = []

    def validate_trade_type(self):
        if self.trade_type and self.trade_type in TRADE_TYPES:
            return 
        raise HTTPException(status_code=400, detail="Invalid trade type")

    def valid_uniqueness(self):
        uniqueness = FclCustomsRate.select(FclCustomsRate.id).where(
            FclCustomsRate.location_id == self.location_id,
            FclCustomsRate.trade_type == self.trade_type,
            FclCustomsRate.container_size == self.container_size,
            FclCustomsRate.container_type == self.container_type,
            FclCustomsRate.commodity == self.commodity,
            FclCustomsRate.service_provider_id == self.service_provider_id,
            FclCustomsRate.importer_exporter_id == self.importer_exporter_id
        ).count()

        if self.id and uniqueness == 1:
            return True
        if not self.id and uniqueness == 0:
            return True
        return False
    
    def validate_container_size(self):
        if self.container_size and self.container_size in CONTAINER_SIZES:
            return
        raise HTTPException(status_code=400, detail="Invalid container size")
    
    def validate_container_type(self):
        if self.container_type and self.container_type in CONTAINER_TYPES:
            return
        raise HTTPException(status_code=400, detail="Invalid container type")
    
    def validate_commodity(self):
      if self.container_type and self.commodity in CONTAINER_TYPE_COMMODITY_MAPPINGS[f"{self.container_type}"]:
        return
      raise HTTPException(status_code=400, detail="Invalid commodity")
    
    def validate_service_provider_id(self):
        if not self.service_provider_id:
            return

        service_provider_data = get_organization(id=self.service_provider_id)
        if len(service_provider_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid service provider ID")
        
    def validate_location_ids(self):
        location_data = maps.list_locations({'filters':{'id': str(self.location_id)}})['list']
        if (len(location_data) != 0) and location_data[0].get('type') in ['seaport', 'country']:
            location_data = location_data[0]
            self.location = location_data
            self.port_id = location_data.get('seaport_id', None)
            self.country_id = location_data.get('country_id', None)
            self.trade_id = location_data.get('trade_id', None)
            self.continent_id = location_data.get('continent_id', None)
            self.location_type = 'port' if location_data.get('type') == 'seaport' else location_data.get('type')
            self.location = {key:value for key,value in location_data.items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}

            return True
        return False
    
    def validate_duplicate_line_items(self):
        unique_items = set()
        for customs_line_item in self.customs_line_items:
            unique_items.add(str(customs_line_item['code']).upper() + str(customs_line_item.get('location_id') or ''))

        if len(self.customs_line_items) != len(unique_items):
            raise HTTPException(status_code=400, detail="Contains Duplicates")
        
    def validate_invalid_line_items(self):
        customs_line_item_codes = [str(t['code']) for t in self.customs_line_items]
        possible_customs_charge_codes = [str(key) for key in self.possible_customs_charge_codes().keys()]

        invalid_customs_line_items = [t for t in customs_line_item_codes if t not in possible_customs_charge_codes]
        if invalid_customs_line_items:
            raise HTTPException(status_code=400, detail="Invalid line items")
        
    def mandatory_charge_codes(self):
        mandatory_charge_codes = [code.upper() for code, config in (self.possible_customs_charge_codes() or {}).items() if 'mandatory' in (config.get('tags') or [])]
        return mandatory_charge_codes
    
    def get_line_items_total_price(self, line_items):
        currency = line_items[0]['currency']
        result = 0.0

        for line_item in line_items:
            result = result + common.get_money_exchange_for_fcl({'from_currency': line_item['currency'], 'to_currency': currency, 'price': line_item['price']})['price']

        return result
    
    def get_mandatory_line_items(self):
        selected_line_items = [line_item for line_item in self.customs_line_items if line_item.get('code').upper() in self.mandatory_charge_codes()]
        return selected_line_items
    
    def set_platform_price(self):
        line_items = self.get_mandatory_line_items()

        if not line_items:
            return
        
        result = self.get_line_items_total_price(line_items)

        rates = FclCustomsRate.select(
            FclCustomsRate.customs_line_items
        ).where(
            FclCustomsRate.location_id == self.location_id,
            FclCustomsRate.trade_type == self.trade_type,
            FclCustomsRate.container_size == self.container_size,
            FclCustomsRate.container_type == self.container_type,
            FclCustomsRate.commodity == self.commodity,
            ((FclCustomsRate.importer_exporter_id == self.importer_exporter_id) | (FclCustomsRate.importer_exporter_id.is_null(True))),
            FclCustomsRate.is_customs_line_items_error_messages_present == False,
            FclCustomsRate.rate_type == self.rate_type,
            ~FclCustomsRate.service_provider_id == self.service_provider_id
        ).execute()

        for rate in rates:
            selected_line_items = [line_item for line_item in rate.customs_line_items if line_item.get('code').upper() in self.mandatory_charge_codes()]
            rate_min_price = 0.0
            currency = selected_line_items[0]['currency']
            for line_item in selected_line_items:
                rate_min_price = rate_min_price + common.get_money_exchange_for_fcl({'price':line_item['price'], 'from_currency':line_item['currency'], 'to_currency':currency})['price']

            if rate_min_price and result > rate_min_price:
                result = rate_min_price

        self.platform_price = result
    
    def set_is_best_price(self):
        if not self.platform_price:
            return
        
        line_items = self.get_mandatory_line_items()
        total_price = self.get_line_items_total_price(line_items)

        self.is_best_price = (total_price <= self.platform_price)

    def update_platform_prices_for_other_service_providers(self):
        from celery_worker import update_fcl_customs_rate_platform_prices_delay
        request = {
            'location_id': self.location_id,
            'trade_type': self.trade_type,
            'container_size': self.container_size,
            'container_type': self.container_type,
            'commodity': self.commodity,
            'importer_exporter_id': self.importer_exporter_id
        }
        update_fcl_customs_rate_platform_prices_delay.apply_async(kwargs = {'request':request}, queue = 'low')

    def detail(self):
        fcl_customs = {
            'customs_line_items': self.customs_line_items,
            'customs_line_items_info_messages': self.customs_line_items_info_messages,
            'is_customs_line_items_info_messages_present': self.is_customs_line_items_info_messages_present,
            'customs_line_items_error_messages': self.customs_line_items_error_messages,
            'is_customs_line_items_error_messages_present': self.is_customs_line_items_error_messages_present,
            'cfs_line_items': self.cfs_line_items,
            'cfs_line_items_info_messages': self.cfs_line_items_info_messages,
            'is_cfs_line_items_info_messages_present': self.is_cfs_line_items_info_messages_present,
            'cfs_line_items_error_messages': self.cfs_line_items_error_messages,
            'is_cfs_line_items_error_messages_present': self.is_cfs_line_items_error_messages_present
        }

        return {'fcl_customs': fcl_customs}

    def possible_customs_charge_codes(self):
        self.set_location()
        fcl_custom_charges = FCL_CUSTOMS_CHARGES
        location = self.location
        
        charge_codes = {}
        for code, config in fcl_custom_charges.items():
            if config.get('condition') is not None and eval(str(config['condition'])) and self.trade_type in config['trade_types'] and 'customs_clearance' in config.get('tags'):
                charge_codes[code] = config
        return charge_codes

    def possible_cfs_charge_codes(self):
        self.set_location()
        fcl_cfs_charges = FCL_CUSTOMS_CHARGES
        location = self.location

        charge_codes = {}
        for code, config in fcl_cfs_charges.items():
            if config.get('condition') is not None and eval(str(config['condition'])) and self.trade_type in config['trade_types'] and 'cfs' in config.get('tags'):
                charge_codes[code] = config
        return charge_codes

    def delete_rate_not_available_entry(self):
        FclCustomsRate.delete().where(
          FclCustomsRate.location_id == self.location_id,
          FclCustomsRate.trade_type == self.trade_type,
          FclCustomsRate.service_provider_id == self.service_provider_id,
          FclCustomsRate.container_size == self.container_size,
          FclCustomsRate.container_type == self.container_type,
          FclCustomsRate.commodity == self.commodity,
          FclCustomsRate.rate_not_available_entry == True
        ).execute() 

    def update_customs_line_item_messages(self):
        if not self.location:
            self.set_location()
        location_ids = list(set([item.get('location_id') for item in self.customs_line_items if item.get('location_id')]))
        locations = []

        if location_ids:
            locations = maps.list_locations({'filters': { 'id': location_ids }})['list']

        self.customs_line_items_error_messages = {}
        self.customs_line_items_info_messages = {}
        self.is_customs_line_items_error_messages_present = False
        self.is_customs_line_items_info_messages_present = False

        grouped_charge_codes = {}

        for line_item in self.customs_line_items:
            grouped_charge_codes[line_item.get('code')] = line_item
        for code, line_items in grouped_charge_codes.items():
            code_config = FCL_CUSTOMS_CHARGES.get(code)

            code_config = {key:value for key,value in code_config.items() if 'customs_clearance' in code_config.get('tags', [])}
            location = self.location
            if not code_config:
                self.customs_line_items_error_messages[code] = ['is invalid']
                self.is_customs_line_items_error_messages_present = True
                continue

            if self.trade_type not in code_config['trade_types']:
                self.customs_line_items_error_messages[code] = [f"can only be added for {', '.join(code_config['trade_types'])}"]
                self.is_customs_line_items_error_messages_present = True
                continue

            if line_items['unit'] not in code_config['units']:
                self.customs_line_items_error_messages[code] = [f"can only be having units {', '.join(code_config['units'])}"]
                self.is_customs_line_items_error_messages_present = True
                continue

            if not eval(str(code_config['condition'])):
                self.customs_line_items_error_messages[code] = ['is invalid']
                self.is_customs_line_items_error_messages_present = True
                continue

            if len(code_config.get('locations', [])) == 0 and line_items.get('location_id') and len(line_items.get('location_id',[])) > 0:
                self.customs_line_items_error_messages[code] = ['can not be added with location']
                self.is_customs_line_items_error_messages_present = True
                continue

            if len(code_config.get('locations', [])) > 0 and line_items.get('location_id') and len(line_items.get('location_id',[])) == 0:
                self.customs_line_items_error_messages[code] = ['can only be added with location']
                self.is_customs_line_items_error_messages_present = True
                continue

            if len(code_config.get('locations', [])) > 0 and ((locations['location_id']['type'] != 'country') or (locations['location_id']['country_code'].upper() == code_config.get('locations', []))):
                self.customs_line_items_error_messages[code] = [f"can only contain locations {', '.join(code_config['locations'])}"]
                self.is_customs_line_items_error_messages_present = True
                continue
        
        possible_customs_charge_codes = self.possible_customs_charge_codes()
        for code, config in possible_customs_charge_codes.items():
            if 'mandatory' in config.get('tags', []):
                if code not in grouped_charge_codes:
                    self.customs_line_items_error_messages[code] = ['is not present']
                    self.is_customs_line_items_error_messages_present = True

            if config.get('locations'):
                location_codes = config.get('locations')
                required_code_specific_locations = maps.list_locations({'filters': { 'id': location_codes }})['list']

                location_names = [value['name'] for key,value in required_code_specific_locations]
                if not location_names:
                    continue

                if not grouped_charge_codes.get(code):
                    self.customs_line_items_info_messages[code] = [f"is required for serving in {', '.join(location_names)}"]
                    self.is_customs_line_items_info_messages_present = True
                else:
                    given_code_specific_location_ids = list(set([t['location_id'] for t in grouped_charge_codes.get(code)]))
                    remaining_code_specific_location_ids = [t for t in required_code_specific_locations.keys() if t not in given_code_specific_location_ids]
                    if not remaining_code_specific_location_ids:
                        self.customs_line_items_info_messages[code] = [f"is required for serving in {', '.join([data['name'] for id, data in required_code_specific_locations.items()])}"]
                        self.is_customs_line_items_info_messages_present = True

            if 'additional_service' in config.get('tags', []) or 'shipment_execution_service' in config.get('tags', []):
                if grouped_charge_codes.get(code) is None:
                    self.customs_line_items_info_messages[code] = ['can be added for more conversion']
                    self.is_customs_line_items_info_messages_present = True

        self.save()

    def update_cfs_line_item_messages(self):
        self.set_location()

        self.cfs_line_items_error_messages = {}
        self.cfs_line_items_info_messages = {}
        self.is_cfs_line_items_error_messages_present = False
        self.is_cfs_line_items_info_messages_present = False

        grouped_charge_codes = {}

        for line_item in self.cfs_line_items:
            grouped_charge_codes[line_item.get('code')] = line_item

        for code, line_items in grouped_charge_codes.items():
            code_config = FCL_CUSTOMS_CHARGES.get(code)

            code_config = {key:value for key,value in code_config.items() if 'cfs' in line_items.get('tags', [])}

            if not code_config:
                self.cfs_line_items_error_messages[code] = ['is invalid']
                self.is_cfs_line_items_error_messages_present = True
                continue

            if self.trade_type not in code_config['trade_types']:
                self.cfs_line_items_error_messages[code] = [f"can only be added for {', '.join(code_config['trade_types'])}"]
                self.is_cfs_line_items_error_messages_present = True
                continue

            if line_items['unit'] not in code_config['units']:
                self.cfs_line_items_error_messages[code] = [f"can only be having units {', '.join(code_config['units'])}"]
                self.is_cfs_line_items_error_messages_present = True
                continue

            if not eval(str(code_config['condition'])):
                self.cfs_line_items_error_messages[code] = ['is invalid']
                self.is_cfs_line_items_error_messages_present = True
                continue

        possible_cfs_charge_codes = self.possible_cfs_charge_codes()
        for code, config in possible_cfs_charge_codes.items():
            if 'mandatory' in config.get('tags', []):
                if code not in grouped_charge_codes:
                    self.cfs_line_items_error_messages[code] = ['is not present']
                    self.is_cfs_line_items_error_messages_present = True

            if 'additional_service' in config.get('tags', []) or 'shipment_execution_service' in config.get('tags', []):
                if grouped_charge_codes.get(code) is None:
                    self.cfs_line_items_info_messages[code] = ['can be added for more conversion']
                    self.is_cfs_line_items_info_messages_present = True

        self.save()

    def validate_before_save(self):
        self.set_location_type()
        self.validate_duplicate_line_items()
        self.validate_invalid_line_items()
        self.validate_trade_type()
        self.validate_container_size()
        self.validate_container_type()
        self.validate_commodity()