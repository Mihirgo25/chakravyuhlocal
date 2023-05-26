from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime, uuid
from micro_services.client import maps, common

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
    importer_exporter_id = UUIDField(index=True)
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

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclCustomsRate, self).save(*args, **kwargs)


    class Meta:
        table_name = 'fcl_customs_rates'

    def set_platform_price(self):
      line_items = self.get_mandatory_line_items()
      if line_items:
        total_price = self.get_line_items_total_price()

        rates_query = FclCustomsRate.select().where(
          FclCustomsRate.location_id == self.location_id,
          FclCustomsRate.trade_type == self.trade_type,
          FclCustomsRate.container_size == self.container_size,
          FclCustomsRate.container_type == self.container_type,
          FclCustomsRate.commodity == self.commodity,
          FclCustomsRate.is_customs_line_items_error_messages_present == False,
          FclCustomsRate.service_provider_id != self.service_provider_id,
          ((FclCustomsRate.importer_exporter_id == self.importer_exporter_id) | (FclCustomsRate.importer_exporter_id.is_null(True)))
        )

        rates = list(rates_query.dicts())

        for rate in rates:
          min_price = rate.customs_line_items.select{ |line_item|
            mandatory_charge_codes.include?(line_item.code.upcase)
          }.map{|t| GetMoneyExchange.run!(price: t.price, from_currency: t.currency, to_currency: currency)[:price].to_i}.sum

          if min_price and total_price > min_price:
            platform_price = min_price

        if platform_price:
          self.is_best_price = (total_price <= platform_price)

        self.platform_price = platform_price

    def get_mandatory_line_items(self):
      for item in self.customs_line_items:
        
      return None

    def get_line_items_total_price(self):
      line_items = self.customs_line_items
      currency = self.customs_line_items[0].get('currency')
      total_price = 0
      for line_item in line_items:
        total_price += common.get_money_exchange_for_fcl({"price": line_item.get('price'), "from_currency": line_item.get('currency'), "to_currency": currency })['price']
      return total_price

    def set_location(self):
        if self.port:
            return

        if not self.port_id:
            return

        location_ids = [str(self.location_id)]

        ports = maps.list_locations({'filters':{'id': location_ids}})['list']
        for port in ports:
            if str(port.get('id')) == str(self.port_id):
                self.country_id = port.get('country_id', None)
                self.trade_id = port.get('trade_id', None)
                self.continent_id = port.get('continent_id', None)
                self.location_ids = [uuid.UUID(str(x)) for x in [self.port_id, self.country_id, self.trade_id, self.continent_id] if x is not None]
                self.port = port
            elif self.main_port_id and str(port.get('id')) == str(self.main_port_id):
                self.main_port = port