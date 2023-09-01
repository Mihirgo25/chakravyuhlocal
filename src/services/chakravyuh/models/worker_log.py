from peewee import Model, CharField
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField, DateTimeField, BigAutoField, TextField
from datetime import datetime


class BaseModel(Model):
    class Meta:
        database = db


class WorkerLog(BaseModel):
    id = BigAutoField()
    status = CharField(default = "started")
    name = CharField(null = True,index = True)
    module_type = CharField()
    module_name = TextField(index = True)
    last_updated_at = DateTimeField(null = True,index = True)
    started_at = DateTimeTZField(default = datetime.utcnow())
    ended_at = DateTimeTZField(null = True)

    class Meta:
        table_name = "worker_logs"
        indexes = (
            (
                (
                    "module_type",
                    "module_name",
                    "last_updated_at",
                    "status"
                ),
                True,
            ),
        )