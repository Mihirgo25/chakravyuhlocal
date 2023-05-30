from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime, uuid
from micro_services.client import maps, common
from configs.fcl_freight_rate_constants import *
from configs.fcl_customs_rate_constants import CONTAINER_TYPE_COMMODITY_MAPPINGS
from database.rails_db import *
from fastapi import HTTPException
# from configs.definitions import FCL_CUSTOMS_CHARGES

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
    importer_exporters_count = IntegerField(null=True)
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

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCustomsRate, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_customs_rates'

    # def set_platform_price(self):
    #   line_items = self.get_mandatory_line_items()
    #   if line_items:
    #     total_price = self.get_line_items_total_price()

    #     rates_query = FclCustomsRate.select().where(
    #       FclCustomsRate.location_id == self.location_id,
    #       FclCustomsRate.trade_type == self.trade_type,
    #       FclCustomsRate.container_size == self.container_size,
    #       FclCustomsRate.container_type == self.container_type,
    #       FclCustomsRate.commodity == self.commodity,
    #       FclCustomsRate.is_customs_line_items_error_messages_present == False,
    #       FclCustomsRate.service_provider_id != self.service_provider_id,
    #       ((FclCustomsRate.importer_exporter_id == self.importer_exporter_id) | (FclCustomsRate.importer_exporter_id.is_null(True)))
    #     )

    #     rates = list(rates_query.dicts())

    #     for rate in rates:
    #       min_price = rate.customs_line_items.select{ |line_item|
    #         mandatory_charge_codes.include?(line_item.code.upcase)
    #       }.map{|t| GetMoneyExchange.run!(price: t.price, from_currency: t.currency, to_currency: currency)[:price].to_i}.sum

    #       if min_price and total_price > min_price:
    #         platform_price = min_price

    #     if platform_price:
    #       self.is_best_price = (total_price <= platform_price)

    #     self.platform_price = platform_price

    # def get_mandatory_line_items(self):
    #   for item in self.customs_line_items:
        
    #   return None

    # def get_line_items_total_price(self):
    #   line_items = self.customs_line_items
    #   currency = self.customs_line_items[0].get('currency')
    #   total_price = 0
    #   for line_item in line_items:
    #     total_price += common.get_money_exchange_for_fcl({"price": line_item.get('price'), "from_currency": line_item.get('currency'), "to_currency": currency })['price']
    #   return total_price

    # def set_location(self):
    #     if self.port:
    #         return

    #     if not self.port_id:
    #         return

    #     location_ids = [str(self.location_id)]

    #     ports = maps.list_locations({'filters':{'id': location_ids}})['list']
    #     for port in ports:
    #         if str(port.get('id')) == str(self.port_id):
    #             self.country_id = port.get('country_id', None)
    #             self.trade_id = port.get('trade_id', None)
    #             self.continent_id = port.get('continent_id', None)
    #             self.location_ids = [uuid.UUID(str(x)) for x in [self.port_id, self.country_id, self.trade_id, self.continent_id] if x is not None]
    #             self.port = port
    #         elif self.main_port_id and str(port.get('id')) == str(self.main_port_id):
    #             self.main_port = port

    def validate_trade_type(self):
        if self.trade_type and self.trade_type in TRADE_TYPES:
            return True
        return False

    def valid_uniqueness(self):
        uniqueness = FclCustomsRate.select().where(
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
            unique_items.add(str(customs_line_item['code']).upper() + str(customs_line_item['location_id']))

        if len(self.customs_line_items) != len(unique_items):
            raise HTTPException(status_code=400, detail="Contains Duplicates")
        
    def validate_invalid_line_items(self):
        customs_line_item_codes = [str(t.code) for t in self.customs_line_items]
        possible_customs_charge_codes = [str(t[0]) for t in self.possible_customs_charge_codes]

        invalid_customs_line_items = [t for t in customs_line_item_codes if t not in possible_customs_charge_codes]
        if invalid_customs_line_items:
            raise HTTPException(status_code=400, detail="Invalid line items")
        
    def mandatory_charge_codes(self):
        mandatory_charge_codes = [code.upper() for code, config in self.possible_customs_charge_codes if 'mandatory' in config.get('tags', [])]
        return mandatory_charge_codes
    
    def get_line_items_total_price(self, line_items):
        currency = line_items[0]['currency']
        result = 0.0

        for line_item in line_items:
            result = result + common.get_money_exchange_for_fcl({'from_currency': line_item['currency'], 'to_currency': currency, 'price': line_item['price']})['price']

        return result
    
    def get_mandatory_line_items(self):
        selected_line_items = [line_item for line_item in self.customs_line_items if line_item.code.upper() in self.mandatory_charge_codes]
        return selected_line_items
    
    def set_platform_price(self):
        line_items = self.get_mandatory_line_items()

        if not line_items:
            return
        
        result = self.get_line_items_total_price(line_items)

        rates = FclCustomsRate.select().where(
            FclCustomsRate.location_id == self.location_id,
            FclCustomsRate.trade_type == self.trade_type,
            FclCustomsRate.container_size == self.container_size,
            FclCustomsRate.container_type == self.container_type,
            FclCustomsRate.commodity == self.commodity,
            ((FclCustomsRate.importer_exporter_id == self.importer_exporter_id) | (FclCustomsRate.importer_exporter_id.is_null(True))),
            FclCustomsRate.is_customs_line_items_error_messages_present == False,
            ~FclCustomsRate.service_provider_id == self.service_provider_id
        )

        for rate in rates:
            selected_line_items = [line_item for line_item in rate.customs_line_items if line_item.code.upper() in self.mandatory_charge_codes]
            rate_min_price = 0.0
            currency = selected_line_items[0]['currency']
            for line_item in selected_line_items:
                rate_min_price = rate_min_price + common.get_money_exchange_for_fcl({'price':line_item['price'], 'from_currency':line_item['currency'], 'to_currency':currency})['price']

            if rate_min_price and result > rate_min_price:
                result = rate_min_price

        self.platform_price = result
        self.save()
    
    def set_is_best_price(self):
        if not self.platform_price:
            return
        
        line_items = self.get_mandatory_line_items()
        total_price = self.get_line_items_total_price(line_items)

        self.is_best_price = (total_price <= self.platform_price)
        self.save()


    # ------------------------------------------------------------------------------------------------

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
    
    def set_location(self):
        if self.location or not self.location_id:
            return
        
        self.location = maps.list_locations({'filters':{'id': [str(self.location_id)]}})['list'][0]
        self.save()

    def possible_customs_charge_codes(self):
        self.set_location()
        # ..

    def delete_rate_not_available_entry(self):
        FclCustomsRate.select().where(
            FclCustomsRate.location_id == self.location_id,
            FclCustomsRate.trade_type == self.trade_type,
            FclCustomsRate.service_provider_id == self.service_provider_id,
            FclCustomsRate.container_size == self.container_size,
            FclCustomsRate.container_type == self.container_type,
            FclCustomsRate.commodity == self.commodity,
            FclCustomsRate.rate_not_available_entry == True
        )

        


    

