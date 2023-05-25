from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from configs.global_constants import EXPORT_CARGO_HANDLING_TYPES
from configs.global_constants import  IMPORT_CARGO_HANDLING_TYPES
import yaml
from configs.definitions import FCL_CFS_CHARGES

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCfsRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    location_id = UUIDField(index=True, null=True)
    country_id = UUIDField(index=True,null=True)
    trade_id = UUIDField(index=True,null=True)
    continent_id = UUIDField(index=True,null=True)
    container_size = CharField(null=True, index=True)
    container_type = CharField(null=True, index=True)
    commodity = CharField(null=True, index=True)
    service_provider_id = UUIDField(index=True,null=True)
    importer_exporter_id = UUIDField(index=True,null=True)
    containers_count = IntegerField(null=True)
    trade_type = CharField(index=True)
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
    location_type= CharField(null=False, index=True)
    cargo_handling_type = CharField(index=True,null=True)


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
            self.errors.append('Code is required.')
        if not self.unit:
            self.errors.append('Unit is required.')
        if not self.price:
            self.errors.append('Price is required.')
        if self.price and self.price < 0:
            self.errors.append('Price must be greater than or equal to 0.')