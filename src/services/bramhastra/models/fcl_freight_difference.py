from peewee import Model, BigIntegerField, FloatField, UUIDField
from database.db_session import db
from playhouse.postgres_ext import TextField, DateTimeTZField


class BaseModel(Model):
    class Meta:
        database = db


class FclFreightDifference(BaseModel):
    id = BigIntegerField()
    statistic_id = BigIntegerField()
    altered_statistic_id = BigIntegerField()
    rate_id = UUIDField()
    altered_rate_id = UUIDField()
    validity_id = UUIDField()
    altered_validity_id = UUIDField()
    bas_standard_price = FloatField()
    altered_bas_standard_price = FloatField()
    object_type = TextField()
    object_id = UUIDField()
    created_at = DateTimeTZField()
    updated_at = DateTimeTZField()

    class Meta:
        table_name = "fcl_freight_differences"
