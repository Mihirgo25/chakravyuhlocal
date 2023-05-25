from peewee import *
from database.db_session import db

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class AirCustomsRateRequests(BaseModel):
    airport_id = UUIDField(null=True)
    booking_params = BinaryJSONField(null=True)
    cargo_readiness_date = DateTimeField(null=True)
    city_id = UUIDField(null=True)
    closed_by_id = UUIDField(null=True)
    closing_remarks = ArrayField(field_class=CharField, null=True)
    commodity = CharField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField()
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    performed_by_id = UUIDField(null=True)
    performed_by_org_id = CharField(null=True)
    performed_by_type = CharField(null=True)
    preferred_customs_rate = DoubleField(null=True)
    preferred_customs_rate_currency = CharField(null=True)
    preferred_detention_free_days = IntegerField(null=True)
    preferred_storage_free_days = IntegerField(null=True)
    remarks = ArrayField(field_class=CharField, null=True)
    request_type = CharField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('air_customs_rate_requests_serial_id_seq'::regclass)")])
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    status = CharField(null=True)
    trade_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField()
    volume = DoubleField(null=True)
    weight = DoubleField(null=True)

    class Meta:
        table_name = 'air_customs_rate_requests'