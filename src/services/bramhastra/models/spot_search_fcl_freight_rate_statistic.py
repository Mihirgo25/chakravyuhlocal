from peewee import Model, BigIntegerField, UUIDField, CharField, IntegerField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, ArrayField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class SpotSearchFclFreightRateStatistic(BaseModel):
    id = BigIntegerField(sequence = 'spot_search_fcl_freight_rate_statistic_seq')
    fcl_freight_rate_statistic_id = BigIntegerField()
    spot_search_id = UUIDField()
    spot_search_fcl_freight_services_id = UUIDField()
    checkout_id = UUIDField(null = True)
    checkout_fcl_freight_rate_services_id = UUIDField(null=True)
    validity_id = UUIDField(null=True)
    rate_id = UUIDField(null=True)
    sell_quotation_id = UUIDField(null=True)
    buy_quotation_id = UUIDField(null=True)
    shipment_id = UUIDField(null=True)
    created_at = DateTimeTZField(default = datetime.utcnow())
    updated_at = DateTimeTZField(default = datetime.utcnow())
    sign = IntegerField(default=1)
    version = IntegerField(default=1)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(SpotSearchFclFreightRateStatistic, self).save(*args, **kwargs)

    class Meta:
        table_name = "spot_search_fcl_freight_rate_statistics"