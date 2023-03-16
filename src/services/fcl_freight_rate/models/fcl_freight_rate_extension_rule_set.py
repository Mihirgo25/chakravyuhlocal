from peewee import * 
from database.db_session import db
from rails_client import client
from configs.fcl_freight_rate_constants import CONTAINER_CLUSTERS
import yaml
from configs.defintions import FCL_FREIGHT_CHARGES
import datetime
from libs.locations import list_location_clusters
class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateExtensionRuleSets(BaseModel):
    cluster_id = CharField(index=True, null=True)
    cluster_reference_name = CharField(index=True, null=True)
    cluster_type = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    extension_name = CharField(null=True)
    gri_currency = CharField(null=True)
    gri_rate = DoubleField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    line_item_charge_code = CharField(index=True, null=True)
    service_provider_id = UUIDField(index=True, null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    status = CharField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateExtensionRuleSets, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_extension_rule_sets'

    def gri_fields(self):
        fcl_freight_charges_dict = FCL_FREIGHT_CHARGES
        if self.line_item_charge_code and self.gri_currency and (self.gri_rate or self.gri_rate == 0):
            if not self.line_item_charge_code in fcl_freight_charges_dict.keys():
                raise Exception('charge code not in list')
            else:
                return True
        elif not self.line_item_charge_code and not self.gri_currency and not (self.gri_rate or self.gri_rate == 0):
            return True
        else:
            raise Exception('all fields charge_code, gri_rate, gri_currency are necessary')

    # def validate_service_provider(self):
    #     if not self.service_provider_id:
    #         return True
    #     service_provider_data = client.ruby.list_organizations({'filters':{'id': str(self.service_provider_id)}})
    #     if service_provider_data.get('account_type') == 'service_provider':
    #         return True
    #     return False

    # def validate_shipping_line(self):
    #     if not self.service_provider_id:
    #         return True
    #     shipping_line_data = client.ruby.list_operators({'filters':{'id': str(self.shipping_line_id)}})
    #     if shipping_line_data.get('operator_type') == 'shipping_line' and self.service_provider_id:
    #         return True
    #     return False

    def validate_uniqueness(self):
        freight_extension_count = FclFreightRateExtensionRuleSets.select().where(
            FclFreightRateExtensionRuleSets.cluster_id == self.cluster_id,
            FclFreightRateExtensionRuleSets.service_provider_id == self.service_provider_id,
            FclFreightRateExtensionRuleSets.shipping_line_id == self.shipping_line_id,
            FclFreightRateExtensionRuleSets.cluster_reference_name == self.cluster_reference_name,
            FclFreightRateExtensionRuleSets.line_item_charge_code == self.line_item_charge_code,
            FclFreightRateExtensionRuleSets.gri_rate == self.gri_rate,
            FclFreightRateExtensionRuleSets.gri_currency == self.gri_currency
        ).count()
        if not freight_extension_count == 0:
            raise Exception('Validate uniqueness error')

    # def validate_trade_type(self):
    #     if self.trade_type in ['import', 'export']:
    #         return True
    #     return False

    # def validate_cluster_type(self):
    #     if self.cluster_type in ['location', 'commodity', 'container']:
    #         return True
    #     return False

    def validate_cluster_id(self):
        if self.cluster_type == 'commodity' and client.ruby.list_fcl_freight_commodity_cluster({'filters':{'id': self.cluster_id}}):
            return
        elif self.cluster_type == 'location' and list_location_clusters({'filters':{'id': self.cluster_id}}):
            return
        elif self.cluster_type == 'container' and self.cluster_id in CONTAINER_CLUSTERS.keys():
            return
        return Exception('Validate Cluster id error')

    def validate_extension_name(self):
        extension_count = FclFreightRateExtensionRuleSets.select().where(
            FclFreightRateExtensionRuleSets.extension_name == self.extension_name,
            FclFreightRateExtensionRuleSets.status == 'active'
        ).count()
        if not extension_count == 0:
            raise Exception('Extension name uniqueness error')

    def validate_all(self):
        # if self.gri_fields() and self.validate_service_provider() and self.validate_shipping_line() and self.valid_uniqueness() and self.validate_trade_type() and self.validate_cluster_type() and self.validate_cluster_id() and self.validate_extension_name():
        self.validate_uniqueness()
        self.validate_extension_name()
        self.validate_cluster_id()