from peewee import Model, UUIDField, CharField, IntegerField, BigIntegerField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, ArrayField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FclFreightRateRequestStatistic(BaseModel):
    id = BigIntegerField(sequence="fcl_freight_rate_request_statistic_seq")
    origin_port_id = UUIDField()
    destination_port_id = UUIDField()
    origin_main_port_id = UUIDField(null=True)
    destination_main_port_id = UUIDField(null=True)
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
    created_at = DateTimeTZField(default=datetime.utcnow())
    updated_at = DateTimeTZField(default=datetime.utcnow())
    importer_exporter_id = UUIDField(null=True)
    closing_remarks = ArrayField(CharField,null = True)
    closed_by_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    request_type = CharField()
    sign = IntegerField(default=1)
    rate_reverted_count = IntegerField(default=0)
    version = IntegerField(default=1)

    class Meta:
        table_name = "fcl_freight_rate_request_statistics"
