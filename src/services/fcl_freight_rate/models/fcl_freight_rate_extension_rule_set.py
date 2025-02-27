from peewee import * 
from database.db_session import db
from configs.fcl_freight_rate_constants import CONTAINER_CLUSTERS
from configs.definitions import FCL_FREIGHT_CHARGES
import datetime
from playhouse.postgres_ext import *
from services.fcl_freight_rate.interaction.list_fcl_freight_commodity_clusters import list_fcl_freight_commodity_clusters
from micro_services.client import maps
from fastapi import HTTPException
class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateExtensionRuleSet(BaseModel):
    cluster_id = CharField(index=True, null=True)
    cluster_reference_name = CharField(index=True, null=True)
    cluster_type = CharField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    extension_name = CharField(index=True, null=True)
    gri_currency = CharField(null=True)
    gri_rate = DoubleField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    line_item_charge_code = CharField(index=True, null=True)
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    shipping_line = BinaryJSONField(null=True)
    status = CharField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateExtensionRuleSet, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_extension_rule_sets'

    def gri_fields(self):
        fcl_freight_charges_dict = FCL_FREIGHT_CHARGES.get()
        if self.line_item_charge_code and self.gri_currency and (self.gri_rate or self.gri_rate == 0):
            if not self.line_item_charge_code in fcl_freight_charges_dict.keys():
                raise HTTPException(status_code=400, detail="charge code not in list")
            else:
                return
        elif not self.line_item_charge_code and not self.gri_currency and not (self.gri_rate or self.gri_rate == 0):
            return
        else:
            raise HTTPException(status_code=400, detail="all fields charge_code, gri_rate, gri_currency are necessary")

    def validate_cluster_id(self):
        if self.cluster_type == 'commodity' and list_fcl_freight_commodity_clusters(filters={'id': self.cluster_id})['list']:
            return
        elif self.cluster_type == 'location' and maps.list_location_cluster({'filters':{'id': self.cluster_id}})['list']:
            return
        elif self.cluster_type == 'container' and self.cluster_id in CONTAINER_CLUSTERS.keys():
            return
        raise HTTPException(status_code=400, detail="Validate Cluster id error")

    def validate_all(self):
        self.gri_fields()
        self.validate_cluster_id()