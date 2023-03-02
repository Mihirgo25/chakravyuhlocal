from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from rails_client import client
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import REQUEST_SOURCES


class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateRequest(BaseModel):
    booking_params = BinaryJSONField(null=True)
    cargo_readiness_date = DateTimeField(null=True)
    cargo_weight_per_container = IntegerField(null=True)
    closed_by_id = UUIDField(null=True)
    closing_remarks = ArrayField(field_class=CharField, null=True)
    commodity = CharField(null=True)
    container_size = CharField(null=True)
    container_type = CharField(null=True)
    containers_count = IntegerField(null=True)
    created_at = DateTimeField()
    destination_continent_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    destination_port_id = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    inco_term = CharField(null=True)
    origin_continent_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    origin_port_id = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    performed_by_id = UUIDField(null=True)
    performed_by_org_id = CharField(null=True)
    performed_by_type = CharField(null=True)
    preferred_detention_free_days = IntegerField(null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    preferred_shipping_line_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    preferred_storage_free_days = IntegerField(null=True)
    remarks = ArrayField(field_class=CharField, null=True)
    request_type = CharField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_requests_serial_id_seq'::regclass)")])
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    status = CharField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'fcl_freight_rate_requests'

    def validate_source(self):
        if self.source and self.source in REQUEST_SOURCES:
            return True
        return False
    
    def validate_source_id(self):
        if self.source == 'spot_search':
            spot_search_data = client.ruby.list_spot_searches({'filters': {'id': [str(self.source_id)]}})['list']
            if len(spot_search_data) != 0:
                return True
            return False
        ###### missing source

    #def validate_performed_by_id
    def validate_performed_by_org_id(self):
        performed_by_org_data = client.ruby.list_organizations({'filters':{'id': [str(self.performed_by_org_id)]}})['list']
        if len(performed_by_org_data) != 0 and performed_by_org_data[0]['account_type'] == 'importer_exporter':
            return True
        return False

    def validate_preferred_shipping_line_ids(self):
        if self.preferred_shipping_line_ids:
            shipping_lines = client.ruby.list_operators()

    