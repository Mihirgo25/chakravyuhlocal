from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from micro_services.client import spot_search, maps

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirCustomsRateRequest(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source = CharField(index=True, null=True)
    source_id = UUIDField(index=True, null=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by_org_id = UUIDField(index=True, null=True)
    performed_by_type = CharField(null=True)
    preferred_customs_rate = DoubleField(null=True)
    preferred_customs_rate_currency = CharField(null=True)
    cargo_readiness_date = DateTimeField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    booking_params = BinaryJSONField(null=True)
    request_type = CharField(null=True)
    status = CharField(index=True, null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    closed_by_id = UUIDField(index=True, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('air_customs_rate_request_serial_id_seq'::regclass)")])
    created_at = DateTimeField(index=True, default = datetime.datetime.now)
    updated_at = DateTimeField(default = datetime.datetime.now)
    weight = FloatField(null = True)
    volume = FloatField(null = True)
    commodity = CharField(null=True)
    country_id = UUIDField(null=True)
    airport_id = UUIDField(null=True)
    trade_id = UUIDField(null=True)
    continent_id = UUIDField(null=True)
    city_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    performed_by = BinaryJSONField(null=True)
    closed_by = BinaryJSONField(null=True)
    spot_search = BinaryJSONField(null=True)
    airport = BinaryJSONField(null=True)

    class Meta:
        table_name = 'air_customs_rate_requests'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirCustomsRateRequest, self).save(*args, **kwargs)
    
    def set_spot_search(self):
        spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})['list']
        self.spot_search = {key:value for key,value in spot_search_data[0].items() if key in ['id', 'importer_exporter_id', 'importer_exporter', 'service_details']}
    
    def set_airport(self):
        airport_data = maps.list_locations({'filters':{'id':str(self.airport_id)}})['list']
        if airport_data:
            self.airport = {key:value for key,value in airport_data[0].items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}