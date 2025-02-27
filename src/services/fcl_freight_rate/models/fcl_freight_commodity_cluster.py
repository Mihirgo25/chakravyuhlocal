from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import FREIGHT_CONTAINER_COMMODITY_MAPPINGS
from fastapi import HTTPException

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightCommodityCluster(BaseModel):
    commodities = JSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    name = CharField(index=True, null=True)
    status = CharField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightCommodityCluster, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_commodity_clusters'

    def validate_commodity_cluster(self):
        for container_type, commodity_names in self.commodities.items():
            for commodity_name in commodity_names:
                if commodity_name not in FREIGHT_CONTAINER_COMMODITY_MAPPINGS[container_type]:
                    raise HTTPException(status_code=400, detail="Invalid commodities")