from peewee import Model, BigIntegerField, CharField, UUIDField, DateField, FloatField
from playhouse.postgres_ext import DateTimeTZField
from database.db_session import db

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateAuditStatistic(BaseModel):
    id = BigIntegerField()
    rate_id = UUIDField()
    created_at = DateTimeTZField()
    origin_continent_id = UUIDField()
    destination_continent_id = UUIDField()
    origin_country_id = UUIDField()
    destination_country_id = UUIDField()
    origin_port_id = UUIDField()
    destination_port_id = UUIDField()
    cogo_entity_id = UUIDField()
    shipping_line_id = UUIDField()
    service_provider_id = UUIDField()
    commodity = CharField()
    container_size = CharField()
    container_type = CharField()
    importer_exporter_id = UUIDField()
    action_name = CharField()
    performed_by_id = UUIDField()
    performed_by_type = CharField()
    currency = CharField()
    code = CharField()
    price = FloatField(default = 0)
    market_price = FloatField(default = 0)
    unit = CharField()
    validity_start = DateField()
    validity_end = DateField()
    sourced_by_id = UUIDField()
    procured_by_id = UUIDField()
    original_price = FloatField(default = 0)
    standard_price = FloatField(default = 0)

    class Meta:
        table_name = "fcl_freight_rate_audit_statistics"
