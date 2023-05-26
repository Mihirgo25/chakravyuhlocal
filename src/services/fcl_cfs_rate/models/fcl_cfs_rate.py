from peewee import * 
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from micro_services.client import maps
from configs.global_constants import EXPORT_CARGO_HANDLING_TYPES
from configs.global_constants import  IMPORT_CARGO_HANDLING_TYPES
import yaml
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
        self.location = location if location['list'] else None
        
        return self.location
    
    def update_line_item_messages(self):
        self.set_location()

        self.line_items_error_messages = {}
        self.line_items_info_messages = {}
        self.is_line_items_error_messages_present = False
        self.is_line_items_info_messages_present = False

        grouped_charge_codes = {}
        # self.line_items.each do |line_item|
        # grouped_charge_codes[line_item.code] = grouped_charge_codes[line_item.code].to_a + [line_item]
        # end
        for line_item in self.line_items:
            if line_item.code not in grouped_charge_codes:
                grouped_charge_codes[line_item.code] = []

            grouped_charge_codes[line_item.code].append(line_item)

        # grouped_charge_codes.each do |code, line_items|
        # code_config = $CHARGES['fcl_cfs_charges'][code.to_sym]
        for code, line_items in grouped_charge_codes.items():
            code_config = FCL_CFS_CHARGES[code]

            if code_config is None:
                self.line_items_error_messages[code] = ['is invalid']
                self.is_line_items_error_messages_present = True
            # next
        # end

        # unless code_config[:trade_types].include?(self.trade_type)
            if not self.trade_type in code_config['trade_types']:
                self.line_items_error_messages[code] = ["can only be added for #{code_config[:trade_types].join(', ')}"]
                self.is_line_items_error_messages_present = True

        # if (line_items.map(&:unit) - code_config[:units]).count > 0
            if len(set(map(lambda x: x.unit, line_items)) - set(code_config["units"])) > 0:
                self.line_items_error_messages[code] = ["can only be having units #{code_config[:units].join(', ')}"]
                self.is_line_items_error_messages_present = True

        # unless eval(code_config[:condition].to_s)
            if not eval(str(code_config["condition"])):
                self.line_items_error_messages[code] = ['is invalid']
                self.is_line_items_error_messages_present = True
        #     next
        # end
        # end

        # possible_charge_codes.select { |_code, config| config[:tags].include?('mandatory') }.each do |code, _config|
        # code = code.to_s
        # if grouped_charge_codes[code].blank?
        #     self.line_items_error_messages[code] = ['is not present']
        #     self.is_line_items_error_messages_present = true
        # end
        # end
        possible_charge_codes_values= self.possible_charge_codes()
        for code, config in filter(lambda x: 'mandatory' in x[1]['tags'], possible_charge_codes_values.items()):
            code = str(code)
            if not grouped_charge_codes.get(code):
                self.line_items_error_messages[code] = ['is not present']
                self.is_line_items_error_messages_present = True

        # possible_charge_codes.select { |_code, config| config[:tags].include?('additional_service') || config[:tags].include?('shipment_execution_service') }.each do |code, _config|
        # code = code.to_s
        # if grouped_charge_codes[code].blank?
        #     self.line_items_info_messages[code] = ['can be added for more conversion']
        #     self.is_line_items_info_messages_present = true
        # end
        # end
        for code, config in filter(lambda x: 'additional_service' in x[1]['tags'] or 'shipment_execution_service' in x[1]['tags'], possible_charge_codes_values.items()):
            code = str(code)
            if not grouped_charge_codes.get(code):
                self.line_items_info_messages[code] = ['can be added for more conversion']
                self.is_line_items_info_messages_present = True

        self.save()

    # end
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
        