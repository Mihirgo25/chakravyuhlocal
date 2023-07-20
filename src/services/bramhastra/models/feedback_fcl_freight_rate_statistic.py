from peewee import Model, UUIDField, CharField, IntegerField, BigIntegerField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FeedbackFclFreightRateStatistic(BaseModel):
    id = BigIntegerField(sequence="feedback_fcl_freight_rate_statistic_seq")
    fcl_freight_rate_statistic_id = BigIntegerField()
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
    service_provider_id = UUIDField(null=True)
    feedback_type = CharField()
    closed_by_id = UUIDField(null=True)
    serial_id = BigIntegerField()
    sign = IntegerField(default=1)
    version = IntegerField(default=1)

    class Meta:
        table_name = "feedback_fcl_freight_rate_statistics"
