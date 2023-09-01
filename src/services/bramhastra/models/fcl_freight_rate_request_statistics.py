from peewee import Model, UUIDField, CharField, IntegerField, BigIntegerField, BooleanField, TextField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, ArrayField
from services.bramhastra.enums import ImportTypes


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FclFreightRateRequestStatistic(BaseModel):
    id = BigIntegerField(sequence="fcl_freight_rate_request_statistic_seq")
    origin_port_id = UUIDField()
    destination_port_id = UUIDField()
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
    container_size = CharField(null=True)
    commodity = CharField(null=True)
    containers_count = IntegerField(null=True)
    is_rate_reverted = BooleanField(default=True)
    created_at = DateTimeTZField(default=datetime.utcnow())
    updated_at = DateTimeTZField(default=datetime.utcnow())
    sign = IntegerField(default=1)
    version = IntegerField(default=1)
    operation_created_at = DateTimeTZField(default=datetime.utcnow())
    operation_updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)

    def save(self, *args, **kwargs):
        self.operation_updated_at = datetime.utcnow()
        return super(FclFreightRateRequestStatistic, self).save(*args, **kwargs)

    CLICK_KEYS = [
        "origin_continent_id",
        "origin_country_id",
        "origin_port_id",
        "rate_request_id",
    ]

    IMPORT_TYPE = ImportTypes.csv.value

    class Meta:
        table_name = "fcl_freight_rate_request_statistics"
