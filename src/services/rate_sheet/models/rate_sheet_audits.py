from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from services.rate_sheet.models.rate_sheet import RateSheet

class BaseModel(Model):
    class Meta:
        database = db

class RateSheetAudit(BaseModel):
    id = UUIDField(
        primary_key=True,
        constraints=[SQL("DEFAULT uuid_generate_v4()")],
        default=uuid.uuid4,
        index=True
    )
    object_type = CharField(null=True)
    object_id = ForeignKeyField(RateSheet, backref="rate_sheet", index=True)
    action_name = CharField(null=True)
    performed_by_id = UUIDField(null=True)
    data = JSONField(null=True)
    procured_by_id = UUIDField(null=True)
    sourced_by_id = UUIDField(null=True)
    performed_by_type = CharField(index=True,null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        table_name = 'rate_sheet_audits'

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(RateSheetAudit, self).save(*args, **kwargs)

RateSheetAudit.add_index(SQL("CREATE INDEX index_rate_sheet_audits_on_object_type_and_object_id ON rate_sheet_audits (object_type, object_id);"))
