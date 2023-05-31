from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from micro_services.client import maps, common
from configs.global_constants import EXPORT_CARGO_HANDLING_TYPES
from configs.global_constants import  IMPORT_CARGO_HANDLING_TYPES
from configs.definitions import FCL_CFS_CHARGES
from fastapi import HTTPException

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
    cfs_line_items = BinaryJSONField(default = [], null=True)
    free_limit = IntegerField(null=True)
    platform_price = IntegerField(null=True)
    is_best_price = BooleanField(null=True)
    is_cfs_line_items_error_messages_present = BooleanField(null=True)
    is_cfs_line_items_info_messages_present = BooleanField(null=True)
    rate_not_available_entry = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    cfs_line_items_error_messages = BinaryJSONField( null=True)
    cfs_line_items_info_messages = BinaryJSONField( null=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    location_type= CharField(null=True, index=True)
    cargo_handling_type = CharField(index=True,null=True)
    importer_exporter_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    procured_by_id = UUIDField(null=True)
    sourced_by_id = UUIDField(null=True)
    procured_by = BinaryJSONField(null=True)
    sourced_by = BinaryJSONField(null=True)
    location = BinaryJSONField(null=True)
    
    class Meta:
        table_name = 'fcl_cfs_rate'


    def validate_cargo_handling_type(self):
            super().validate()
            if self.trade_type == 'export' and self.cargo_handling_type not in EXPORT_CARGO_HANDLING_TYPES:
                self.errors.append('Invalid cargo_handling_type for export.')
            if self.trade_type == 'import' and self.cargo_handling_type not in IMPORT_CARGO_HANDLING_TYPES:
                self.errors.append('Invalid cargo_handling_type for import.')
    def possible_charge_codes(self):
        fcl_cfs_charges = FCL_CFS_CHARGES
        filtered_charge_codes = {}
        for code, config in fcl_cfs_charges.items():
            if (
                self.trade_type in config['trade_types']
                and self.cargo_handling_type in config['tags']
                and config['condition']
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
        
        location = maps.list_locations({ 'filters': { 'id': self.location_id } })
        if location['list']:
            self.location = location
            self.location_type = 'port' if location.get('type') == 'seaport' else location.get('type')
        
        else:
            None

    
    def mandatory_charge_codes(self):
        return [
            code.upper() for code, config in self.possible_charge_codes.items()
            if 'mandatory' in config['tags']
        ]


    def get_mandatory_cfs_line_items(self):
        return [
            line_item for line_item in self.cfs_line_items
            if line_item.code.upper() in self.mandatory_charge_codes()
        ]


    def get_cfs_line_items_total_price(self):
        cfs_line_items = self.cfs_line_items
        currency = self.cfs_line_items[0].get('currency')
        total_price = 0
        for line_item in cfs_line_items:
            total_price += common.get_money_exchange_for_fcl({"price": line_item.get('price'), "from_currency": line_item.get('currency'), "to_currency": currency })['price']
        return total_price
    
    def set_platform_price(self):
        cfs_line_items = self.get_mandatory_cfs_line_items()

        if not cfs_line_items:
            return

        result = self.get_cfs_line_items_total_price()

        rates_query = FclCfsRate.select().where(
            (FclCfsRate.location_id == self.location_id),
            (FclCfsRate.trade_type == self.trade_type),
            (FclCfsRate.container_size == self.container_size),
            (FclCfsRate.container_type == self.container_type),
            (FclCfsRate.commodity == self.commodity),
            (FclCfsRate.service_provider_id != self.service_provider_id),
            ((FclCfsRate.importer_exporter_id == self.importer_exporter_id) | (FclCfsRate.importer_exporter_id.is_null(True))),
            (FclCfsRate.cargo_handling_type == self.cargo_handling_type)
        )
        
        rates = list(rates_query.dicts())

        for rate in rates:
            rate_min_price=0
            currency = self.cfs_line_items[0].get('currency')
            for line_item in rate.cfs_line_items:
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
        from celery_worker import update_cfs_rate_platform_prices
        request = {
            'location_id': self.location_id,
            'trade_type': self.trade_type,
            'container_size': self.container_size,
            'container_type': self.container_type,
            'commodity': self.commodity,
            'importer_exporter_id': self.importer_exporter_id,
            'cargo_handling_type': self.cargo_handling_type
        }
        update_cfs_rate_platform_prices.apply_async(kwargs = {'request':request}, queue = 'low')
        
    
    def update_line_item_messages(self):
        self.set_location()

        self.cfs_line_items_error_messages = {}
        self.cfs_line_items_info_messages = {}
        self.is_cfs_line_items_error_messages_present = False
        self.is_cfs_line_items_info_messages_present = False

        grouped_charge_codes = {}

        for line_item in self.cfs_line_items:
            if line_item["code"] not in grouped_charge_codes:
                grouped_charge_codes[line_item["code"]] = []

            grouped_charge_codes[line_item["code"]].append(line_item)

        for code, line_items in grouped_charge_codes.items():
            code_config = FCL_CFS_CHARGES[code]

            if code_config is None:
                self.cfs_line_items_error_messages[code] = ['is invalid']
                self.is_cfs_line_items_error_messages_present = True

            if not self.trade_type in code_config['trade_types']:
                self.cfs_line_items_error_messages[code] = ["can only be added for #{code_config[:trade_types].join(', ')}"]
                self.is_cfs_line_items_error_messages_present = True

            if len(set(map(lambda x: x["unit"], line_items)) - set(code_config["units"])) > 0:
                self.cfs_line_items_error_messages[code] = ["can only be having units #{code_config[:units].join(', ')}"]
                self.is_cfs_line_items_error_messages_present = True

            if not eval(str(code_config["condition"])):
                self.cfs_line_items_error_messages[code] = ['is invalid']
                self.is_cfs_line_items_error_messages_present = True

        possible_charge_codes_values= self.possible_charge_codes()
        for code, config in filter(lambda x: 'mandatory' in x[1]['tags'], possible_charge_codes_values.items()):
            code = str(code)
            if not grouped_charge_codes.get(code):
                self.cfs_line_items_error_messages[code] = ['is not present']
                self.is_cfs_line_items_error_messages_present = True

        for code, config in filter(lambda x: 'additional_service' in x[1]['tags'] or 'shipment_execution_service' in x[1]['tags'], possible_charge_codes_values.items()):
            code = str(code)
            if not grouped_charge_codes.get(code):
                self.cfs_line_items_info_messages[code] = ['can be added for more conversion']
                self.is_cfs_line_items_info_messages_present = True

        self.save()

        return True

class FclCfsRateLineItem(Model):
    code = CharField()
    unit = CharField()
    price = DecimalField(decimal_places=2)
    currency = CharField()
    remarks = ArrayField(CharField)
    slabs = ArrayField(CharField)

    class Meta:
        database = db

    def validate(self):
        super().validate()
        if not self.code:
           raise HTTPException( status_code =401 ,detail = 'Code is required.')
        if not self.unit:
            raise HTTPException( status_code =401 ,detail ='Unit is required.')
        if not self.price:
            raise HTTPException( status_code =401 ,detail ='Price is required.')
        if self.price and self.price < 0:
            raise HTTPException( status_code =401 ,detail = 'Price cannot  be negative')
        