from peewee import (
    Model,
    UUIDField,
    CharField,
    IntegerField,
    BigIntegerField,
    FloatField,
    BooleanField
)
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, ArrayField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FeedbackAirFreightRateStatistic(BaseModel):
    id = BigIntegerField(sequence="feedback_air_freight_rate_statistic_seq")
    air_freight_rate_statistic_id = BigIntegerField()
    feedback_id = UUIDField()
    validity_id = UUIDField()
    rate_id = UUIDField()
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    performed_by_id = UUIDField(null=True)
    performed_by_org_id = UUIDField(null=True)
    created_at = DateTimeTZField(default=datetime.utcnow())
    updated_at = DateTimeTZField(default=datetime.utcnow())
    importer_exporter_id = UUIDField(null=True)
    preferred_freight_rate = FloatField(null=True)
    currency = CharField(default = "USD")
    feedbacks = ArrayField(CharField, null=True)
    closing_remarks = ArrayField(CharField, null=True)
    service_provider_id = UUIDField(null=True)
    feedback_type = CharField()
    closed_by_id = UUIDField(null=True)
    status = CharField(default="active")
    serial_id = BigIntegerField()
    sign = IntegerField(default=1)
    version = IntegerField(default=1)
    operation_created_at = DateTimeTZField(default=datetime.utcnow())
    operation_updated_at = DateTimeTZField(default=datetime.utcnow())
    is_rate_reverted = BooleanField()

    class Meta:
        table_name = "feedback_air_freight_rate_statistics"
