from peewee import *
from rails_client import client
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import TRADE_TYPES


STATUSES = ('active', 'inactive')

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateLocalAgents(BaseModel):
    created_at = DateTimeField(default=datetime.datetime.now)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    location_id = UUIDField(index=True, null=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    location_type = UUIDField(null=True)
    service_provider_id = UUIDField(index=True, null=True)
    status = CharField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'fcl_freight_rate_local_agents'
        indexes = (
            (('location_id', 'trade_type'), True),
        )

    def validate_service_provider(self):
        service_provider_data = client.ruby.list_organizations({'filters':{'id': self.service_provider_id}})['list'][0]
        if service_provider_data.get('account_type') == 'service_provider':
            return True
        return False
    
    def set_location_ids_and_type(self):
        location_data = client.ruby.list_locations({'filters':{'id': self.location_id}})['list'][0]
        if location_data.get('type') in ['seaport', 'country', 'trade']:
          country_id = location_data.get('country_id')
          trade_id = location_data.get('trade_id')
          continent_id = location_data.get('continent_id')
          self.location_ids = list(filter(None, [self.location_id, country_id, trade_id, continent_id]))
          self.location_type = 'port' if location_data.get('type') == 'seaport' else location_data.get('type')
          return True
        return False
    
    def validate_trade_type(self):
      if self.trade_type and self.trade_type in TRADE_TYPES:
        return True
      return False
    
    def validate_status(self):
       if self.status in STATUSES:
          return True
       return False
    
    def valid_uniqueness(self):
        freight_weight_limit_cnt = FclFreightRateLocalAgents.select().where(
            FclFreightRateLocalAgents.location_id == self.location_id,
            FclFreightRateLocalAgents.trade_type == self.trade_type,
        ).count()

        if self.id and freight_weight_limit_cnt==1:
            return True
        if not self.id and freight_weight_limit_cnt==0:
            return True
        return False