import datetime
from fastapi import HTTPException
from peewee import *
from playhouse.postgres_ext import *
from configs.definitions import FCL_CFS_CHARGES
from configs.fcl_cfs_rate_constants import CONTAINER_TYPE_COMMODITY_MAPPINGS,FREE_DAYS_TYPES, EXPORT_CARGO_HANDLING_TYPES, IMPORT_CARGO_HANDLING_TYPES
from configs.global_constants import CONTAINER_SIZES, CONTAINER_TYPES, TRADE_TYPES
from database.db_session import db
from database.rails_db import *
from micro_services.client import common, maps
from configs.fcl_freight_rate_constants import RATE_TYPES

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCfsRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    location_id = UUIDField(index=True, null=True)
    country_id = UUIDField(index=True,null=True)
    trade_id = UUIDField(index=True,null=True)
    continent_id = UUIDField(null=True)
    container_size = CharField(null=True, index=True)
    container_type = CharField(null=True, index=True)
    commodity = CharField(null=True)
    service_provider_id = UUIDField(index=True,null=True)
    importer_exporter_id = UUIDField(null=True)
    containers_count = IntegerField(null=True)
    trade_type = CharField(index=True, null= True)
    line_items = BinaryJSONField(default = [], null=True)
    free_limit = IntegerField(null=True)
    platform_price = IntegerField(null=True)
    is_best_price = BooleanField(null=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    line_items_error_messages = BinaryJSONField( null=True)
    line_items_info_messages = BinaryJSONField( null=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    location_type= CharField(null=True, index=True)
    cargo_handling_type = CharField(index=True,null=True)
    service_provider = BinaryJSONField(null=True)
    procured_by_id = UUIDField(null=True)
    sourced_by_id = UUIDField(null=True)
    procured_by = BinaryJSONField(null=True)
    sourced_by = BinaryJSONField(null=True)
    location = BinaryJSONField(null=True)
    free_days = BinaryJSONField(null=True)
    importer_exporter = BinaryJSONField(null=True)
    mode = CharField(default = 'manual', null = True)
    tags = BinaryJSONField(null=True)
    rate_type = CharField(default='market_place', choices = RATE_TYPES)
    accuracy = FloatField(default = 100, null = True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCfsRate, self).save(*args, **kwargs)
    
    class Meta:
        table_name = 'fcl_cfs_rates'

    def validate_mandatory_free_days(self):
        free_days = [free_day.get('free_days_type') for free_day in self.free_days]

        required_free_days = set(
            t['type'] for t in FREE_DAYS_TYPES if 'mandatory' in t['tags']
         ) - set(free_days)

        if required_free_days:
            error_message = f"{', '.join(required_free_days)} is required"
            raise HTTPException(status_code=400, detail=error_message)

    
    def validate_duplicate_line_items(self):
        unique_items = set()
        for cfs_line_item in self.line_items:
            unique_items.add(str(cfs_line_item['code']).upper() + str(cfs_line_item.get('location_id')))

        if len(self.line_items) != len(unique_items):
            raise HTTPException(status_code=400, detail="Contains Duplicates")
        
    def validate_invalid_line_items(self):
        cfs_line_item_codes = [str(t['code']) for t in self.line_items]
        possible_cfs_charge_codes = [str(t) for t in self.possible_cfs_charge_codes()]
        invalid_customs_line_items = [t for t in cfs_line_item_codes if t not in possible_cfs_charge_codes]
        if invalid_customs_line_items:
            raise HTTPException(status_code=400, detail="Invalid line items")

    def validate_cargo_handling_type(self):
            super().validate()
            if self.trade_type == 'export' and self.cargo_handling_type not in EXPORT_CARGO_HANDLING_TYPES:
                raise HTTPException(status_code=400,detail='Invalid cargo_handling_type for export')
            if self.trade_type == 'import' and self.cargo_handling_type not in IMPORT_CARGO_HANDLING_TYPES:
                raise HTTPException(status_code=400,detail='Invalid cargo_handling_type for import')

    def possible_cfs_charge_codes(self):
        self.set_location()
        location = self.location
        fcl_cfs_charges = FCL_CFS_CHARGES
        filtered_charge_codes = {}
        for code, config in fcl_cfs_charges.items():
            if (
                self.trade_type in config['trade_types']
                and self.cargo_handling_type in config['tags']
                and eval(config['condition'])
            ):
                filtered_charge_codes[code] = config

        return filtered_charge_codes

    def delete_rate_not_available_entry(self):
        FclCfsRate.delete().where(
            FclCfsRate.trade_type == self.trade_type,
            FclCfsRate.location_id == self.location_id,
            FclCfsRate.service_provider_id == self.service_provider_id,
            FclCfsRate.container_size == self.container_size,
            FclCfsRate.container_type == self.container_type,
            FclCfsRate.commodity == self.commodity,
            FclCfsRate.cargo_handling_type == self.cargo_handling_type,
            FclCfsRate.rate_not_available_entry == True
            ).execute()
    
    def set_location(self):
        if self.location is not None or self.location_id is None:
            return True
        
        location = maps.list_locations({ 'filters': { 'id': str(self.location_id) } })
        if location['list']:
            location_data = location['list'][0]
            self.location = location_data
            self.location_type = location_data.get('type') if self.location_type is None else self.location_type
            self.country_id = uuid.UUID(location_data.get('country_id')) if self.country_id is None else self.country_id
            self.trade_id = uuid.UUID(location_data.get('trade_id')) if self.trade_id is None else self.trade_id
            self.continent_id = uuid.UUID(location_data.get('continent_id')) if self.continent_id is None else self.continent_id
            self.location_ids = [self.location_id,self.country_id,self.trade_id,self.continent_id]

    def validate_before_save(self):
        self.validate_duplicate_line_items()
        self.validate_invalid_line_items()
        self.validate_trade_type()
        self.validate_container_size()
        self.validate_container_type()
        self.validate_commodity()

    def mandatory_cfs_charge_codes(self):
        return [
            code.upper() for code, config in (self.possible_cfs_charge_codes() or {}).items()
            if 'mandatory' in (config['tags'] or [])
        ]


    def get_mandatory_cfs_line_items(self):

        selected_line_items =     [line_item for line_item in self.line_items
            if line_item.get('code').upper() in self.mandatory_cfs_charge_codes()
        ]
        return selected_line_items


    def get_cfs_line_items_total_price(self):
        line_items = self.line_items
        currency = self.line_items[0].get('currency')
        total_price = 0
        for line_item in line_items:
            total_price += common.get_money_exchange_for_fcl({"price": line_item.get('price'), "from_currency": line_item.get('currency'), "to_currency": currency })['price']
        return total_price
    
    def set_platform_price(self):
        line_items = self.get_mandatory_cfs_line_items()

        if not line_items:
            return

        result = self.get_cfs_line_items_total_price()

        rates_query = FclCfsRate.select(
                    FclCfsRate.line_items
            ).where(
            (FclCfsRate.location_id == self.location_id),
            (FclCfsRate.trade_type == self.trade_type),
            (FclCfsRate.container_size == self.container_size),
            (FclCfsRate.container_type == self.container_type),
            (FclCfsRate.commodity == self.commodity),
            (FclCfsRate.rate_type == self.rate_type),
            (FclCfsRate.service_provider_id != self.service_provider_id),
            ((FclCfsRate.importer_exporter_id == self.importer_exporter_id) | (FclCfsRate.importer_exporter_id.is_null(True))),
            (FclCfsRate.cargo_handling_type == self.cargo_handling_type)
        )
        
        rates = list(rates_query.dicts())

        for rate in rates:
            rate_min_price=0
            currency = self.line_items[0].get('currency')

            for line_item in rate.get('line_items'):
                rate_min_price += common.get_money_exchange_for_fcl({"price": line_item.get('price'), "from_currency": line_item.get('currency'), "to_currency": currency })['price']
            
            if rate_min_price is not None and result > rate_min_price:
                result = rate_min_price

        self.platform_price = result

    def set_is_best_price(self):
        if self.platform_price is None:
            return

        total_price = self.get_cfs_line_items_total_price()

        self.is_best_price = (total_price <= self.platform_price)
    
    def update_platform_prices_for_other_service_providers(self):
        from celery_worker import update_fcl_cfs_rate_platform_prices_delay
        request = {
            'location_id': self.location_id,
            'trade_type': self.trade_type,
            'container_size': self.container_size,
            'container_type': self.container_type,
            'commodity': self.commodity,
            'importer_exporter_id': self.importer_exporter_id,
            'cargo_handling_type': self.cargo_handling_type
        }
        update_fcl_cfs_rate_platform_prices_delay.apply_async(kwargs = {'request':request}, queue = 'low')
        
    
    def update_line_item_messages(self):
        self.set_location()

        self.line_items_error_messages = {}
        self.line_items_info_messages = {}
        self.is_line_items_error_messages_present = False
        self.is_line_items_info_messages_present = False

        grouped_charge_codes = {}

        for line_item in self.line_items:
            if line_item["code"] not in grouped_charge_codes:
                grouped_charge_codes[line_item["code"]] = []

            grouped_charge_codes[line_item.get("code")].append(line_item)
 
        for code, line_items in grouped_charge_codes.items():
            code_config = FCL_CFS_CHARGES.get(code)

            if code_config is None:
                self.line_items_error_messages[code] = ['is invalid']
                self.is_line_items_error_messages_present = True

            if not self.trade_type in code_config['trade_types']:
                self.line_items_error_messages[code] = [f"can only be added for {', '.join(code_config['trade_types'])}"]
                self.is_line_items_error_messages_present = True

            if len(set(map(lambda x: x["unit"], line_items)) - set(code_config["units"])) > 0:
                self.line_items_error_messages[code] = [f"can only be having units {', '.join(code_config['units'])}"]
                self.is_line_items_error_messages_present = True

            if not eval(str(code_config["condition"])):
                self.line_items_error_messages[code] = ['is invalid']
                self.is_line_items_error_messages_present = True

        possible_charge_codes_values= self.possible_cfs_charge_codes()
        for code, config in filter(lambda x: 'mandatory' in x[1]['tags'], possible_charge_codes_values.items()):
            code = str(code)
            if not grouped_charge_codes.get(code):
                self.line_items_error_messages[code] = ['is not present']
                self.is_line_items_error_messages_present = True             

        for code, config in filter(lambda x: 'additional_service' in x[1]['tags'] or 'shipment_execution_service' in x[1]['tags'], possible_charge_codes_values.items()):
            code = str(code)
            if not grouped_charge_codes.get(code):
                self.line_items_info_messages[code] = ['can be added for more conversion']
                self.is_line_items_info_messages_present = True

        self.save()
      
    def validate_trade_type(self):
            if self.trade_type and self.trade_type in TRADE_TYPES:
                return True
            return False

    def valid_uniqueness(self): 
        uniqueness = FclCfsRate.select().where(
            FclCfsRate.location_id == self.location_id,
            FclCfsRate.trade_type == self.trade_type,
            FclCfsRate.container_size == self.container_size,
            FclCfsRate.container_type == self.container_type,
            FclCfsRate.commodity == self.commodity,
            FclCfsRate.service_provider_id == self.service_provider_id,
            FclCfsRate.importer_exporter_id == self.importer_exporter_id
        ).count()
        if self.id and uniqueness == 1:
            return True
        if not self.id and uniqueness == 0:
            return True
        return False
        
    def validate_container_size(self):
        if self.container_size and self.container_size in CONTAINER_SIZES:
            return True
        return False
        
    def validate_container_type(self):
        if self.container_type and self.container_type in CONTAINER_TYPES:
            return True
        return False
        
    def validate_commodity(self):
        if self.container_type and self.commodity in CONTAINER_TYPE_COMMODITY_MAPPINGS[f"{self.container_type}"]:
            return True
        return False
        
    def validate_service_provider_id(self):
        if not self.service_provider_id:
            return
        service_provider_data = get_organization(id=self.service_provider_id)
        if len(service_provider_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid service provider ID")
        
        return True

    def detail(self):
        return {
            'fcl_cfs':{
            'line_items':self.line_items,
            'line_items_info_messages':self.line_items_info_messages,
            'is_line_items_info_messages_present':self.is_line_items_info_messages_present,
            'line_items_error_messages':self.line_items_error_messages,
            'is_line_items_error_messages_present':self.is_line_items_error_messages_present,
            'cargo_handling_type':self.cargo_handling_type
            }
        }