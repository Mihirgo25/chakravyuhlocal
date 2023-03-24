from configs.fcl_freight_rate_constants import TRADE_TYPES
from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
import uuid
from micro_services.client import *
from database.rails_db import *

STATUSES = ('active', 'inactive')

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateLocalAgent(BaseModel):
    created_at = DateTimeField(default=datetime.datetime.now)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    location_id = UUIDField(index=True, null=True)
    location = BinaryJSONField(null=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    location_type = CharField(null=True)
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)
    status = CharField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateLocalAgent, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_local_agents'

    def validate_service_provider(self):
        service_provider_data = get_service_provider(str(self.service_provider_id))
        if len(service_provider_data) > 0 :
            service_provider_data = service_provider_data[0]
            service_provider_data['id'] = str(service_provider_data['id'])
            self.service_provider = service_provider_data
            if service_provider_data.get('account_type') != 'service_provider':
                raise HTTPException(status_code=400, detail="Invalid Account Type - Not Service Provider")
        else:
            raise HTTPException(status_code=400, detail="Service Provider Id Invalid")
        return True
    
    def set_location_ids_and_type(self):
        location_data = maps.list_locations({'filters':{'id': str(self.location_id)}})
        if 'list' in location_data and len(location_data['list']) > 0:
            location_data = location_data['list'][0]
            if location_data.get('type') in ['seaport', 'country', 'trade']:
                country_id = location_data.get('country_id')
                trade_id = location_data.get('trade_id')
                continent_id = location_data.get('continent_id')
                self.location_ids = list(filter(None, [uuid.UUID(self.location_id), uuid.UUID(country_id), uuid.UUID(trade_id), uuid.UUID(continent_id)]))
                self.location_type = 'port' if location_data.get('type') == 'seaport' else location_data.get('type')
                self.location = {key:value for key,value in location_data.items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}
        else:
            raise HTTPException(status_code=400, detail="location Id Invalid")

    
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