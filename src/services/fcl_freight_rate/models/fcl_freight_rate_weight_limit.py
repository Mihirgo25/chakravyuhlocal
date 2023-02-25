from peewee import *
from rails_client import client
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import CONTAINER_SIZES, CONTAINER_TYPES, LOCATION_PAIR_HIERARCHY
from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate


LOCATION_TYPES = ('seaport', 'country', 'trade', 'continent')

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateWeightLimit(BaseModel):
    container_size = CharField(null=True)
    container_type = CharField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    destination_continent_id = UUIDField(index=True, null=True)
    destination_country_id = UUIDField(index=True, null=True)
    destination_location_id = UUIDField(null=True)
    destination_location_type = CharField(null=True)
    destination_port_id = UUIDField(index=True, null=True)
    destination_trade_id = UUIDField(index=True, null=True)
    free_limit = DoubleField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    is_slabs_missing = BooleanField(null=True)
    origin_continent_id = UUIDField(index=True, null=True)
    origin_country_id = UUIDField(index=True, null=True)
    origin_destination_location_type = CharField(index=True, null=True)
    origin_location_id = UUIDField(null=True)
    origin_location_type = CharField(null=True)
    origin_port_id = UUIDField(index=True, null=True)
    origin_trade_id = UUIDField(index=True, null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    service_provider_id = UUIDField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    slabs = BinaryJSONField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'fcl_freight_rate_weight_limits'
        indexes = (
            (('container_size', 'container_type'), False),
            (('origin_location_id', 'destination_location_id', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id'), True),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type'), False),
            (('updated_at', 'service_provider_id', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'shipping_line_id', 'is_slabs_missing'), False),
        )

    def validate_origin_location(self):
        origin_location_data = client.ruby.list_locations({'filters':{'id': self.origin_location_id}})['list'][0]
        if origin_location_data.get('type') in LOCATION_TYPES:
            self.origin_port_id = origin_location_data.get('seaport_id', None)
            self.origin_country_id = origin_location_data.get('country_id', None)
            self.origin_trade_id = origin_location_data.get('trade_id', None)
            self.origin_continent_id = origin_location_data.get('continent_id', None)
            self.origin_location_type = 'port' if origin_location_data.get('type') == 'seaport' else origin_location_data.get('type')
            return True
        return False

    def validate_destination_location(self):
        destination_location_data = client.ruby.list_locations({'filters':{'id': self.destination_location_id}})['list'][0]
        if destination_location_data.get('type') in LOCATION_TYPES:
            self.destination_port_id = destination_location_data.get('seaport_id', None)
            self.destination_country_id = destination_location_data.get('country_id', None)
            self.destination_trade_id = destination_location_data.get('trade_id', None)
            self.destination_continent_id = destination_location_data.get('continent_id', None)
            self.destination_location_type = 'port' if destination_location_data.get('type') == 'seaport' else destination_location_data.get('type')
            self.origin_destination_location_type = str(self.origin_location_type) + ':' + str(self.destination_location_type)
            return True
        return False

    def validate_shipping_line(self):
      shipping_line_data = client.ruby.list_operators({'filters':{'id': self.shipping_line_id}})['list'][0]
      if shipping_line_data.get('operator_type') == 'shipping_line':#Can we check like this as we are getting through id so we will get only single row or should we send it as a param filter
        return True
      return False

    def validate_service_provider(self):
      service_provider_data = client.ruby.list_organizations({'filters':{'id': self.service_provider_id}})['list'][0]
      if service_provider_data.get('account_type') == 'service_provider':
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

    def valid_uniqueness(self):
        freight_weight_limit_cnt = FclFreightRateWeightLimit.select().where(
            FclFreightRateWeightLimit.origin_location_id == self.origin_location_id,
            FclFreightRateWeightLimit.destination_location_id == self.destination_location_id,
            FclFreightRateWeightLimit.container_size == self.container_size,
            FclFreightRateWeightLimit.container_type == self.container_type,
            FclFreightRateWeightLimit.shipping_line_id == self.shipping_line_id,
            FclFreightRateWeightLimit.service_provider_id == self.service_provider_id
        ).count()

        if self.id and freight_weight_limit_cnt==1:
            return True
        if not self.id and freight_weight_limit_cnt==0:
            return True
        return False

    # def validate_free_limit(self):
    #   if 'free_limit' in self:
    #     return True
    #   return False

    def update_freight_objects(self):
        origin_destination_location_types = [key for key in LOCATION_PAIR_HIERARCHY.keys() if LOCATION_PAIR_HIERARCHY[key] >= LOCATION_PAIR_HIERARCHY[self.origin_destination_location_type]]

        freight_query = FclFreightRate.where(
        FclFreightRate.container_size == self.container_size,
        FclFreightRate.container_type == self.container_type,
        FclFreightRate.shipping_line_id == self.shipping_line_id,
        FclFreightRate.service_provider_id == self.service_provider_id
        ).where(
            eval("FclFreightRate.origin_{self.origin_location_type}_id == self.origin_location_id"),
            eval("FclFreightRate.destination_#{self.destination_location_type}_id == self.destination_location_id")
        )

        freight_query.join(FclFreightRateWeightLimit, on=(FclFreightRate.weight_limit_id == FclFreightRateWeightLimit.id)).where(FclFreightRateWeightLimit.origin_destination_location_type == origin_destination_location_types)

        print(freight_query)