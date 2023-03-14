from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from rails_client import client
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import REQUEST_SOURCES
import datetime


class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateLocalRequest(BaseModel):
    booking_params = BinaryJSONField(null=True)
    cargo_readiness_date = DateField(null=True)
    closed_by_id = UUIDField(null=True)
    closing_remarks = ArrayField(field_class=CharField, null=True)
    commodity = CharField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    main_port_id = UUIDField(null=True)
    performed_by_id = UUIDField(null=True)
    performed_by_org_id = UUIDField(null=True)
    performed_by_type = CharField(null=True)
    port_id = UUIDField(null=True)
    preferred_detention_free_days = IntegerField(null=True)
    preferred_rate = DoubleField(null=True)
    preferred_rate_currency = CharField(null=True)
    preferred_shipping_line_ids = ArrayField(field_class=UUIDField, null=True)
    remarks = ArrayField(field_class=CharField, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_local_requests_serial_id_seq'::regclass)")])
    shipping_line_id = UUIDField(null=True)
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    status = CharField(null=True)
    trade_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateLocalRequest, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_local_requests'

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
    #def validate_closed_by_id

    def validate_before_save(self):
        if not self.validate_source():
            raise HTTPException(status_code=499, detail="incorrect source")

        if not self.validate_source_id(self):
            raise HTTPException(status_code=499, detail="invalid source id")

        if not self.validate_performed_by_org_id(self):
            raise HTTPException(status_code=499, detail="incorrect performed by id")
        
        # return True

    def send_closed_notifications_to_sales_agent(self):
        #########################
        location_pair = FclFreightRateLocalRequest.select(FclFreightRateLocalRequest.port_id).where(FclFreightRateLocalRequest.source_id == self.source_id).first()
