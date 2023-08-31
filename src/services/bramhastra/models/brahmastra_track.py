from peewee import Model, CharField
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, DateTimeField, BigAutoField
from datetime import datetime


class BaseModel(Model):
    class Meta:
        database = db


class BrahmastraTrack(BaseModel):
    id = BigAutoField()
    status = CharField(default = "started")
    table_name = CharField()
    last_updated_at = DateTimeField(null = True)
    started_at = DateTimeTZField(default = datetime.utcnow())
    ended_at = DateTimeTZField(null = True)

    class Meta:
        table_name = "brahmastra_tracks"