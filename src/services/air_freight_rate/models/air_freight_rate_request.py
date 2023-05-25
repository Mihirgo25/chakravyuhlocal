from peewee import *
from database.db_session import db

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class AirFreightRateRequests(BaseModel):
    booking_params = BinaryJSONField(null=True)
    cargo_readiness_date = DateTimeField(null=True)
    cargo_stacking_type = CharField(null=True)
    closed_by_id = UUIDField(null=True)
    closing_remarks = ArrayField(field_class=CharField, null=True)
    commodity = CharField(null=True)
    commodity_sub_type = CharField(null=True)
    commodity_type = CharField(null=True)
    created_at = DateTimeField()
    destination_airport_id = UUIDField(null=True)
    destination_continent_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    inco_term = CharField(null=True)
    origin_airport_id = UUIDField(null=True)
    origin_continent_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    packages = BinaryJSONField(null=True)
    packages_count = IntegerField(null=True)
    performed_by_id = UUIDField(null=True)
    performed_by_org_id = CharField(null=True)
    performed_by_type = CharField(null=True)
    preferred_airline_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    preferred_detention_free_days = IntegerField(null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    preferred_storage_free_days = IntegerField(null=True)
    remarks = ArrayField(field_class=CharField, null=True)
    request_type = CharField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('air_freight_rate_requests_serial_id_seq'::regclass)")])
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    status = CharField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField()
    volume = DoubleField(null=True)
    weight = DoubleField(null=True)

    class Meta:
        table_name = 'air_freight_rate_requests'