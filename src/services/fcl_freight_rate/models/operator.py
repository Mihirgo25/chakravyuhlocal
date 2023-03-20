from peewee import *
from playhouse.postgres_ext import *
from database.db_session import db_rails

class BaseModel(Model):
    class Meta:
        database = db_rails

class Operator(BaseModel):
    business_name = CharField(null=True)
    country_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    created_at = DateTimeField()
    iata_code = CharField(null=True)
    icao_code = CharField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    is_nvocc = BooleanField(constraints=[SQL("DEFAULT false")], null=True)
    line_code = CharField(null=True)
    logo_url = CharField(null=True)
    masked_name = CharField(null=True)
    operator_type = CharField(null=True)
    short_name = CharField(null=True)
    status = CharField(null=True)
    updated_at = DateTimeField()
    web_url = CharField(null=True)

    class Meta:
        table_name = 'operators'
        indexes = (
            (('line_code', 'operator_type'), False),
        )