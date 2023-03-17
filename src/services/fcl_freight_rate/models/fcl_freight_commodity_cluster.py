from peewee import *
from database.db_session import db
import datetime
from playhouse.postgres_ext import *
from rails_client import client
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.fcl_freight_rate_constants import FREIGHT_CONTAINER_COMMODITY_MAPPINGS
from configs.fcl_freight_rate_constants import *
import yaml
from rails_client import client
from fastapi import HTTPException

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightCommodityCluster(BaseModel):
    commodities = JSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    name = CharField(null=True)
    status = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightCommodityCluster, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_commodity_clusters'
        indexes = (
            (('name', 'status'), True),
        )

    def validate_uniqueness(self):
        query = (
        FclFreightCommodityCluster.select()
        .where(FclFreightCommodityCluster.name == self.name)
        .where(FclFreightCommodityCluster.status == 'active')).count()

        if self.id and query==1:
            return True
        if not self.id and query==0:
            return True
        return False

    def validate_commodity_cluster(self):
        for container_type, commodity_names in self.commodities.items():
            for commodity_name in commodity_names:
                if commodity_name not in FREIGHT_CONTAINER_COMMODITY_MAPPINGS[container_type]:
                    raise HTTPException(status_code=400, detail="Invalid commodities")

    def validate(self):
        if not self.validate_uniqueness():
            raise HTTPException(status_code=400, detail="Commodity cluster already exists")
        self.validate_commodity_cluster()
