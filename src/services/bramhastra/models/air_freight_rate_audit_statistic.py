from peewee import Model, CharField, UUIDField, DateField, FloatField, BigAutoField, IntegerField
from playhouse.postgres_ext import DateTimeTZField
from database.db_session import db

class BaseModel(Model):
    class Meta:
        database = db

class AirFreightRateAuditStatistic(BaseModel):
    id = BigAutoField(primary_key = True)
    rate_id = UUIDField(index = True)
    created_at = DateTimeTZField()
    origin_continent_id = UUIDField(null = True)
    destination_continent_id = UUIDField(null = True)
    origin_country_id = UUIDField(null = True)
    destination_country_id = UUIDField(null = True)
    origin_airport_id = UUIDField(index = True)
    destination_airport_id = UUIDField(index = True)
    cogo_entity_id = UUIDField(null = True)
    airline_id = UUIDField(index = True)
    service_provider_id = UUIDField()
    commodity = CharField()
    commodity_type = CharField()
    commodity_subtype = CharField()
    container_size = CharField()
    container_type = CharField()
    importer_exporter_id = UUIDField(null = True)
    action_name = CharField()
    performed_by_id = UUIDField(index = True)
    performed_by_type = CharField(null = True)
    currency = CharField(null = True)
    code = CharField(null = True)
    price = FloatField(default = 0)
    market_price = FloatField(default = 0)
    unit = CharField(null = True)
    validity_start = DateField()
    validity_end = DateField()
    sourced_by_id = UUIDField(null = True)
    procured_by_id = UUIDField(null = True)
    original_price = FloatField(default = 0)
    standard_price = FloatField(default = 0)
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

    class Meta:
        table_name = "air_freight_rate_audit_statistics"
