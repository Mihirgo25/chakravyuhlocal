from peewee import Model, BigIntegerField
from database.db_session import db
from playhouse.postgres_ext import DateTimeTZField


class BaseModel(Model):
    class Meta:
        database = db


class DataMigration(BaseModel):
    id = BigIntegerField()
    created_at = DateTimeTZField()

    class Meta:
        table_name = "data_migrations"
