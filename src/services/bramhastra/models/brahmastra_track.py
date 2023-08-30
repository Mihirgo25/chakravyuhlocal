from peewee import Model, BigIntegerField, CharField
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, DateTimeField
from datetime import datetime


class BaseModel(Model):
    class Meta:
        database = db


class BrahmastraTrack(BaseModel):
    id = BigIntegerField()
    service = CharField()
    status = CharField(default = "started")
    table_name = CharField()
    last_updated_at = DateTimeField()
    started_at = DateTimeTZField(default = datetime.utcnow())
    ended_at = DateTimeTZField(null = True)

    class Meta:
        table_name = "brahmastra_tracks"