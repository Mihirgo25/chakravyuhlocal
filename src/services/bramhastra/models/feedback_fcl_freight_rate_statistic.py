from peewee import Model, BigAutoField, UUIDField, CharField, IntegerField
import datetime
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FeedbackFclFreightRateStatistic(BaseModel):
    id = BigAutoField()
    feedback_id = UUIDField()
    validity_id = UUIDField()
    source = CharField()
    source_id = CharField()
    performed_by_id = CharField()
    performed_by_org_id = CharField()
    rate_id = UUIDField()
    created_at = DateTimeTZField()
    updated_at = DateTimeTZField()
    importer_exporter_id = CharField()
    feedback_type = CharField()
    closed_by_id = UUIDField()
    serial_id = IntegerField()
    state = IntegerField(default=1)
    version = IntegerField()

    class Meta:
        table_name = "feedback_fcl_freight_rate_statistics"
