from configs.fcl_freight_rate_constants import TRADE_TYPES
from peewee import *
from rails_client import client
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
import uuid

STATUSES = ('active', 'inactive')

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateLocalAgent(BaseModel):
    created_at = DateTimeField(default=datetime.datetime.now)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    location_id = UUIDField(index=True, null=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    location_type = UUIDField(null=True)
    service_provider_id = UUIDField(index=True, null=True)
    status = CharField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateLocalAgent, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_local_agents'
        indexes = (
            (('location_id', 'trade_type'), True),
        )

    def validate_service_provider(self):
        service_provider_data = client.ruby.list_organizations({'filters':{'id': str(self.service_provider_id)}})
        if 'list' in service_provider_data and len(service_provider_data['list']) > 0 :
            service_provider_data = service_provider_data['list'][0]
            if service_provider_data.get('account_type') != 'service_provider':
                raise HTTPException(status_code=400, detail="Invalid Account Type - Not Service Provider")
        else:
            raise HTTPException(status_code=400, detail="Service Provider Id Invalid")
        return True
    
    def set_location_ids_and_type(self):
        location_data = client.ruby.list_locations({'filters':{'id': str(self.location_id)}})
        if 'list' in location_data and len(location_data['list']) > 0:
            location_data = location_data['list'][0]
            if location_data.get('type') in ['seaport', 'country', 'trade']:
                country_id = location_data.get('country_id')
                trade_id = location_data.get('trade_id')
                continent_id = location_data.get('continent_id')
                self.location_ids = list(filter(None, [uuid.UUID(self.location_id), uuid.UUID(country_id), uuid.UUID(trade_id), uuid.UUID(continent_id)]))
                self.location_type = 'port' if location_data.get('type') == 'seaport' else location_data.get('type')
        else:
            raise HTTPException(status_code=400, detail="Service Provider Id Invalid")

    
    def validate_trade_type(self):
      if not (self.trade_type and self.trade_type in TRADE_TYPES):
            raise HTTPException(status_code=400, detail="Invalid trade_type")

    
    def validate_status(self):

        if self.status not in STATUSES:
            raise HTTPException(status_code=400, detail="Invalid status")
        return True


    
    def validate_uniqueness(self):
        freight_weight_limit_cnt = FclFreightRateLocalAgent.select().where(
            FclFreightRateLocalAgent.location_id == self.location_id,
            FclFreightRateLocalAgent.trade_type == self.trade_type,
        ).count()
        ####################### check this

        # if self.id and freight_weight_limit_cnt==1:
        #     return True
        # if not self.id and freight_weight_limit_cnt==0:
        #     return True
        if freight_weight_limit_cnt != 0:
            raise HTTPException(status_code=400, detail="Location_id and trade_type are not unique")

    
    def validate(self):
        self.validate_service_provider()
        self.validate_trade_type()
        self.validate_status()
        self.validate_uniqueness()
        return True

    # def save(self, *args, **kwargs):
    #     self.validate()
    #     return super().save(*args, **kwargs)