from peewee import Model, BigAutoField, UUIDField, CharField, IntegerField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, BinaryJSONField
from services.bramhastra.database.sql import Sql
from playhouse.signals import post_save

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class QuotationFclFreightRateStatistic(BaseModel):
    id = BigAutoField()
    validity_id = UUIDField()
    rate_id = UUIDField()
    spot_search_id = UUIDField()
    spot_search_fcl_freight_services_id = UUIDField()
    checkout_id = UUIDField()
    checkout_fcl_freight_rate_services_id = UUIDField(null=True)
    sell_quotation_id = UUIDField()
    buy_quotation_id = UUIDField()
    shipment_id = UUIDField(null=True)
    shipment_fcl_freight_rate_services_id = UUIDField(null=True)
    cancellation_reason = CharField(default = '')
    is_active = CharField()
    created_at = DateTimeTZField(default = datetime.utcnow())
    updated_at = DateTimeTZField(default = datetime.utcnow())
    status = CharField(default = 'active')
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

    class Meta:
        table_name = "quotation_fcl_freight_rate_statistics"

def on_table_created(sender, instance, created):
    breakpoint()
    if created:
        breakpoint()
        table_name = sender._meta.table_name
        clickhouse_table = Sql()
        clickhouse_table.run(table_name)

        print(f"Table '{table_name}' created or new record inserted!")
        
post_save.connect(on_table_created, sender=QuotationFclFreightRateStatistic)