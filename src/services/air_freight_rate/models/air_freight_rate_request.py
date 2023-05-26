from peewee import *
from database.db_session import db
from configs.air_freight_rate_constants import REQUEST_SOURCES
from fastapi import HTTPException
from micro_services.client import *
from database.rails_db import *
from playhouse.postgres_ext import *

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class AirFreightRateRequest(BaseModel):
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


    def validate(self):
        # self.validate_source()
        # self.validate_source_id()
        # self.validate_performed_by_id()
        # self.validate_performed_by_org_id()
        self.validate_preferred_shipping_line_ids()
        return True

    def validate_source(self):
        if self.source and self.source not in REQUEST_SOURCES:
            raise HTTPException(status_code=400, detail="Invalid source")


    def validate_source_id(self):
        if self.source == 'spot_search':
            spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})['list']
            if len(spot_search_data) == 0:
                raise HTTPException(status_code=400, detail="Invalid Source ID")

    def validate_performed_by_id(self):
        data = get_user(str(self.performed_by_id))

        if data:
            pass
        else:
            raise HTTPException(status_code=400, detail='Invalid Performed by ID')

    def validate_performed_by_org_id(self):
        performed_by_org_data = get_organization(id=str(self.performed_by_org_id))
        if len(performed_by_org_data) == 0 or performed_by_org_data[0]['account_type'] != 'importer_exporter':
            raise HTTPException(status_code=400, detail='Invalid Account Type')

    def validate_preferred_airline_ids(self):
        if not self.preferred_airline_ids:
            pass
        if self.preferred_airline_ids:
            # need to change the name to get operators name
            airline_data = get_shipping_line(id=self.preferred_airline_ids)
            if len(airline_data) != len(self.preferred_airline_ids):
                raise HTTPException(status_code=400, detail='Invalid Shipping Line ID')
            self.preferred_shipping_lines = airline_data
            self.preferred_shipping_line_ids = [uuid.UUID(str(ariline_id)) for ariline_id in self.preferred_airline_ids]

