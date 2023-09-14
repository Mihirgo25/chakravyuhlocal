from peewee import Model, BigIntegerField, UUIDField, IntegerField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, BigAutoField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class SpotSearchFclFreightRateStatistic(BaseModel):
    id = BigAutoField(primary_key = True)
    fcl_freight_rate_statistic_id = BigIntegerField(index = True)
    spot_search_id = UUIDField(index = True)
    spot_search_fcl_freight_services_id = UUIDField(index = True)
    checkout_id = UUIDField(null = True, index = True)
    checkout_fcl_freight_rate_services_id = UUIDField(null=True, index = True)
    validity_id = UUIDField(null=True, index = True)
    rate_id = UUIDField(null=True, index = True)
    sell_quotation_id = UUIDField(null=True)
    buy_quotation_id = UUIDField(null=True)
    shipment_id = UUIDField(null=True, index = True)
    created_at = DateTimeTZField(default = datetime.utcnow())
    updated_at = DateTimeTZField(default = datetime.utcnow(), index = True)
    sign = IntegerField(default=1)
    version = IntegerField(default=1)
    operation_created_at = DateTimeTZField(default=datetime.utcnow())
    operation_updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)

    def save(self, *args, **kwargs):
        self.operation_updated_at = datetime.utcnow()
        return super(SpotSearchFclFreightRateStatistic, self).save(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(SpotSearchFclFreightRateStatistic, self).save(*args, **kwargs)

    class Meta:
        table_name = "spot_search_fcl_freight_rate_statistics"