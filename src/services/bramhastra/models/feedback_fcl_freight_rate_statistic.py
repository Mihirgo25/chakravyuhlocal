from peewee import Model, UUIDField, CharField, IntegerField, BigIntegerField
from datetime import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, ArrayField,FloatField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FeedbackFclFreightRateStatistic(BaseModel):
    id = BigIntegerField(sequence="feedback_fcl_freight_rate_statistic_seq")
    fcl_freight_rate_statistic_id = BigIntegerField(index = True)
    feedback_id = UUIDField(index = True)
    validity_id = UUIDField(index = True)
    rate_id = UUIDField(index = True)
    source = CharField(null=True)
    source_id = UUIDField(null=True, index = True)
    performed_by_id = UUIDField(null=True, index = True)
    performed_by_org_id = UUIDField(null=True, index = True)
    created_at = DateTimeTZField(default=datetime.utcnow())
    updated_at = DateTimeTZField(default=datetime.utcnow(), index = True)
    importer_exporter_id = UUIDField(null=True, index = True)
    preferred_freight_rate = FloatField(default=0)
    currency = CharField(null = True)
    feedbacks = ArrayField(CharField, null=True)
    closing_remarks = ArrayField(CharField, null=True)
    service_provider_id = UUIDField(null=True, index = True)
    feedback_type = CharField()
    closed_by_id = UUIDField(null=True, index = True)
    status = CharField(default="active")
    serial_id = BigIntegerField(index = True)
    sign = IntegerField(default=1)
    version = IntegerField(default=1)
    operation_created_at = DateTimeTZField(default=datetime.utcnow())
    operation_updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)

    def save(self, *args, **kwargs):
        self.operation_updated_at = datetime.utcnow()
        return super(FeedbackFclFreightRateStatistic, self).save(*args, **kwargs)

    class Meta:
        table_name = "feedback_fcl_freight_rate_statistics"
