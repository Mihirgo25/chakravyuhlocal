from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from fastapi import HTTPException
from micro_services.client import *
from database.rails_db import *

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
    # preferred_detention_free_days = IntegerField(null=True)
    # preferred_storage_free_days = IntegerField(null=True)
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
    # preferred_airline_ids = ArrayField(field_class=UUIDField, null=True, constraints=[SQL("DEFAULT '{}'::uuid[]")])
    # preferred_airlines = BinaryJSONField(null = True)

    class Meta:
        table_name = 'air_customs_rate_requests'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirCustomsRateRequest, self).save(*args, **kwargs)
    
    def set_spot_search(self):
        spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})['list']
        self.spot_search = {key:value for key,value in spot_search_data[0].items() if key in ['id', 'importer_exporter_id', 'importer_exporter', 'service_details']}
    
    def set_airport(self):
        airport_data = maps.list_locations({'filters':{'id':self.airport_id}})['list']
        if airport_data:
            self.airport = {key:value for key,value in airport_data[0].items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}
    
    # def validate_preferred_airline_ids(self):
    #     if not self.preferred_airline_ids:
    #         pass

    #     if self.preferred_airline_ids:
    #         preferred_airlines = []
    #         for airline_id in self.preferred_airline_ids:
    #             airline_data = get_shipping_line(id=airline_id)
    #             if len(airline_data) == 0:
    #                 raise HTTPException(status_code=400, detail='Invalid Shipping Line ID')
    #             preferred_airlines.append(airline_data[0])
    #         self.preferred_airlines = preferred_airlines

    def validate_before_save(self):
        # self.validate_preferred_airline_ids()
        return True