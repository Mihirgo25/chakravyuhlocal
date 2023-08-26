from peewee import Model, UUIDField, CharField, IntegerField, BigIntegerField, BooleanField, TextField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, ArrayField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class AirFreightRateRequestStatistic(BaseModel):
    id = BigIntegerField(sequence="air_freight_rate_request_statistic_seq")
    origin_airport_id = UUIDField()
    destination_airport_id = UUIDField()
    origin_region_id = UUIDField(null=True)
    destination_region_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    origin_continent_id = UUIDField(null=True)
    destination_continent_id = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    origin_pricing_zone_map_id = UUIDField(null=True)
    destination_pricing_zone_map_id = UUIDField(null=True)
    rate_request_id = UUIDField()
    validity_ids = ArrayField(UUIDField,null = True)
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    performed_by_id = UUIDField(null=True)
    performed_by_org_id = UUIDField(null=True)
    importer_exporter_id = UUIDField(null=True)
    closing_remarks = ArrayField(TextField,null = True)
    closed_by_id = UUIDField(null=True)
    request_type = CharField(null=True)
    commodity = CharField(null=True)
    commodity_type = CharField(null=True)
    commodity_sub_type = CharField(null=True)
    packages_count = IntegerField(null=True)
    is_rate_reverted = BooleanField(default=True)
    created_at = DateTimeTZField(default=datetime.utcnow())
    updated_at = DateTimeTZField(default=datetime.utcnow())
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

    class Meta:
        table_name = "air_freight_rate_request_statistics"
