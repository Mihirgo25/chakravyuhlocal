from peewee import *
from rails_client import client
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import SPECIFICITY_TYPE, FREE_DAYS_TYPES, TRADE_TYPES, CONTAINER_SIZES, CONTAINER_TYPES, LOCATION_HIERARCHY
from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from services.fcl_freight_rate.models.fcl_freight_rate_locals import FclFreightRateLocal


class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateFreeDay(BaseModel):
    container_size = CharField(null=True)
    container_type = CharField(index=True, null=True)
    continent_id = UUIDField(index=True, null=True)
    country_id = UUIDField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    free_days_type = CharField(index=True, null=True)
    free_limit = IntegerField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporter_id = UUIDField(null=True)
    is_slabs_missing = BooleanField(null=True)
    location_id = UUIDField(null=True)
    location_type = CharField(index=True, null=True)
    port_id = UUIDField(index=True, null=True)
    previous_days_applicable = BooleanField(null=True)
    rate_not_available_entry = BooleanField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    service_provider_id = UUIDField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    slabs = BinaryJSONField(null=True)
    specificity_type = CharField(null=True)
    trade_id = UUIDField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'fcl_freight_rate_free_days'
        indexes = (
            (('container_size', 'container_type'), False),
            (('importer_exporter_id', 'service_provider_id'), False),
            (('rate_not_available_entry', 'location_id', 'trade_type', 'free_days_type', 'container_size', 'container_type', 'shipping_line_id', 'service_provider_id', 'specificity_type', 'importer_exporter_id'), False),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'free_days_type', 'port_id'), False),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'port_id'), False),
            (('service_provider_id', 'shipping_line_id', 'container_size', 'container_type', 'trade_type', 'free_days_type', 'port_id'), False),
            (('updated_at', 'id', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id'), False),
            (('updated_at', 'service_provider_id', 'free_days_type', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'free_days_type', 'port_id'), False),
            (('updated_at', 'service_provider_id', 'free_days_type', 'shipping_line_id', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'free_days_type', 'trade_type', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'port_id'), False),
            (('updated_at', 'service_provider_id', 'shipping_line_id', 'is_slabs_missing'), False),
            (('updated_at', 'service_provider_id', 'trade_type', 'is_slabs_missing'), False),
        )

    def set_location_ids_and_type(self):
        location_data = client.ruby.list_locations({'filters':{'id': self.location_id}})['list'][0]
        if location_data.get('type') in ['seaport', 'country', 'trade', 'continent']:
          self.port_id = location_data.get('seaport_id',None)
          self.country_id = location_data.get('country_id', None)
          self.trade_id = location_data.get('trade_id', None)
          self.continent_id = location_data.get('continent_id', None)
          self.location_type = 'port' if location_data.get('type') == 'seaport' else location_data.get('type')
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

    def validate_importer_exporter(self):
      importer_exporter_data = client.ruby.list_organizations({'filters':{'id': self.importer_exporter_id}})['list'][0]
      if importer_exporter_data.get('account_type') == 'importer_exporter':
        return True
      return False

    def validate_specificity_type(self):
      if self.specificity_type and self.specificity_type in SPECIFICITY_TYPE:
        return True
      return False
    
    def validate_free_days_type(self):
      if self.free_days_type and self.free_days_type in FREE_DAYS_TYPES:
        return True
      return False
    
    def validate_trade_type(self):
      if self.trade_type and self.trade_type in TRADE_TYPES:
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

    # def validate_free_limit(self):
    #   if 'free_limit' in self:
    #     return True
    #   return False
    
    def valid_uniqueness(self):
      freight_free_day_cnt = FclFreightRateFreeDay.select().where(
        FclFreightRateFreeDay.location_id == self.location_id,
        FclFreightRateFreeDay.trade_type == self.trade_type,
        FclFreightRateFreeDay.free_days_type == self.free_days_type,
        FclFreightRateFreeDay.container_size == self.container_size,
        FclFreightRateFreeDay.container_type == self.container_type,
        FclFreightRateFreeDay.shipping_line_id == self.shipping_line_id,
        FclFreightRateFreeDay.service_provider_id == self.service_provider_id,
        FclFreightRateFreeDay.importer_exporter_id == self.importer_exporter_id,
        FclFreightRateFreeDay.specificity_type == self.specificity_type
      ).count()

      if self.id and freight_free_day_cnt==1:
        return True
      if not self.id and freight_free_day_cnt==0:
        return True

      return False
    
  #   def update_special_attributes
  #   self.update_columns(is_slabs_missing: self.slabs.to_a.empty?)
  # end

  # def update_local_objects
  #   return if self.importer_exporter_id.present?

  #   location_types = FclFreightRateConstants::LOCATION_HIERARCHY.select { |_location_type, score| score >= FclFreightRateConstants::LOCATION_HIERARCHY[self.location_type] }.map(&:first)

  #   local_query = FclFreightRateLocal.where(
  #     trade_type: self.trade_type,
  #     container_size: self.container_size,
  #     container_type: self.container_type,
  #     shipping_line_id: self.shipping_line_id,
  #     service_provider_id: self.service_provider_id
  #   ).where(
  #     "#{self.location_type}_id" => self.location_id
  #   )

  #   local_query.joins("inner join fcl_freight_rate_free_days local_#{self.free_days_type}s on local_#{self.free_days_type}s.id = fcl_freight_rate_locals.#{self.free_days_type}_id").where(
  #     "local_#{self.free_days_type}s" => {
  #       location_type: location_types
  #     }
  #   ).update_all("#{self.free_days_type}_id" => self.id)

  #   local_query.where("#{self.free_days_type}_id" => nil).update_all("#{self.free_days_type}_id" => self.id)
  # end

    def update_local_objects(self):
      if self.importer_exporter_id:
        return
      
      location_types = [key for key in LOCATION_HIERARCHY.keys() if LOCATION_HIERARCHY[key] >= LOCATION_HIERARCHY[self.location_type]]

      local_query = FclFreightRateLocal.where(
      FclFreightRateLocal.trade_type == self.trade_type,
      FclFreightRateLocal.container_size == self.container_size,
      FclFreightRateLocal.container_type == self.container_type,
      FclFreightRateLocal.shipping_line_id == self.shipping_line_id,
      FclFreightRateLocal.service_provider_id == self.service_provider_id
      # eval("FclFreightRateLocal.{self.location_type}_id == self.location_id")
	  ).where(eval("FclFreightRateLocal.{self.location_type}_id == self.location_id"))


    def update_freight_objects(self):
      if self.trade_type == 'export' and self.free_days_type == 'demurrage':    #######################
        return
      
      location_types = [key for key in LOCATION_HIERARCHY.keys() if LOCATION_HIERARCHY[key] >= LOCATION_HIERARCHY[self.location_type]]

      location_key = 'origin' if self.trade_type == 'export' else 'destination'

      freight_query = FclFreightRate.where(
      FclFreightRate.container_size == self.container_size,
      FclFreightRate.container_type == self.container_type,
      FclFreightRate.shipping_line_id == self.shipping_line_id,
      FclFreightRate.service_provider_id == self.service_provider_id
      ).where(eval("FclFreightRate.{}_{}_id == self.location_id".format(location_key,self.location_type)))


