from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
import datetime
from micro_services.client import *
from database.rails_db import *

class BaseModel(Model):
    # db.execute_sql('create sequence fcl_freight_rate_requests_serial_id_seq')
    class Meta:
        database = db
        only_save_dirty = True

class HaulageFreightRateRequest(BaseModel):
    booking_params = BinaryJSONField(null=True)
    cargo_readiness_date = DateTimeField(null=True)
    cargo_weight_per_container = IntegerField(null=True)
    closed_by_id = UUIDField(index=True, null=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)
    commodity = CharField(index=True, null=True)
    container_size = CharField(index=True, null=True)
    container_type = CharField(index=True, null=True)
    containers_count = IntegerField(null=True)
    created_at = DateTimeField(index=True, default = datetime.datetime.now)
    destination_city_id = UUIDField( null=True)
    destination_country_id = UUIDField( null=True)
    destination_location_id = UUIDField(index=True, null=True)
    destination_location = BinaryJSONField(null=True)
    destination_cluster_id = UUIDField( null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_city_id = UUIDField( null=True)
    origin_country_id = UUIDField( null=True)
    origin_location_id = UUIDField(index=True, null=True)
    origin_location = BinaryJSONField(null=True)
    origin_cluster_id = UUIDField( null=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by = BinaryJSONField(null=True)
    performed_by_org_id = UUIDField(index=True, null=True)
    performed_by_type = CharField(index=True, null=True)
    preferred_detention_free_days = IntegerField(null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    preferred_shipping_line_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    preferred_shipping_lines = BinaryJSONField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)
    request_type = CharField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('haulage_freight_rate_request_serial_id_seq'::regclass)")])
    source = CharField( null=True)
    source_id = UUIDField(index=True ,null=True)
    status = CharField(index=True, null=True)
    updated_at = DateTimeField(default = datetime.datetime.now)
    reverted_rates_count = IntegerField(null=True)
    reverted_by_user_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    expiration_time = DateTimeField(null = True)
    trade_type = CharField(index=True, null=True)


    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(HaulageFreightRateRequest, self).save(*args, **kwargs)

    class Meta:
        table_name = 'haulage_freight_rate_requests'


    # def validate_source(self):
    #     if self.source and self.source not in REQUEST_SOURCES:
    #         raise HTTPException(status_code=400, detail="Invalid source")


    def validate_source_id(self):
        if self.source == 'spot_search':
            spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})['list']
            if len(spot_search_data) == 0:
                raise HTTPException(status_code=400, detail="Invalid Source ID")

    def validate_performed_by_id(self):
        data = get_user(self.performed_by_id)

        if data!={}:
            pass
        else:
            raise HTTPException(status_code=400, detail='Invalid Performed by ID')

    def validate_performed_by_org_id(self):
        performed_by_org_data = get_organization(id=str(self.performed_by_org_id))
        if len(performed_by_org_data) == 0 or performed_by_org_data[0]['account_type'] != 'importer_exporter':
            raise HTTPException(status_code=400, detail='Invalid Account Type')