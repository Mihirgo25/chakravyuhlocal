from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from services.fcl_customs_rate.models.fcl_customs_rate import FclCustomsRate
from configs.fcl_customs_rate_constants import FEEDBACK_SOURCES, FEEDBACK_TYPES
from micro_services.client import spot_search, checkout
from database.rails_db import *
from configs.definitions import FCL_CUSTOMS_CURRENCIES

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCustomsRateFeedback(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source = CharField(index=True, null=True)
    source_id = UUIDField(null=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by_org_id = UUIDField(null=True)
    performed_by_type = CharField(index=True, null=True)
    preferred_customs_rate = DoubleField(null=True)
    preferred_customs_rate_currency = CharField(null=True)
    feedbacks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)
    fcl_customs_rate_id = UUIDField(null=True,index=True)
    validity_id = UUIDField(null=True)
    outcome = CharField(null=True)
    outcome_object_id = UUIDField(null=True)
    booking_params = BinaryJSONField(null=True)
    feedback_type = CharField(index=True, null=True)
    status = CharField(index=True, null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)
    closed_by_id = UUIDField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_customs_rate_feedback_serial_id_seq'::regclass)")])
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    performed_by = BinaryJSONField(null=True)
    location = BinaryJSONField(null=True)
    closed_by = BinaryJSONField(null=True)
    organization = BinaryJSONField(null=True)
    spot_search = BinaryJSONField(null=True)
    service_provider = BinaryJSONField(null=True)
    location_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    port_id = UUIDField(null=True)
    trade_id = UUIDField(null=True)
    commodity = CharField(null=True, index=True)
    service_provider_id = UUIDField(null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCustomsRateFeedback, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_customs_rate_feedbacks'

    def validate_fcl_customs_rate_id(self):
        fcl_customs_rate_data = FclCustomsRate.get(**{'id' : self.fcl_customs_rate_id})
        if fcl_customs_rate_data:
            return True
        return False
    
    def validate_source(self):
        if self.source and self.source in FEEDBACK_SOURCES:
            return True
        return False
    
    def validate_source_id(self):
        if self.source == 'spot_search':
            spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})
            if 'list' in spot_search_data and len(spot_search_data['list']) != 0:
                return True
            
        if self.source == 'checkout':
            checkout_data = checkout.list_checkouts({'filters':{'id': [str(self.source_id)]}})
            if 'list' in checkout_data and len(checkout_data['list']) != 0:
                return True
        return False
    
    def validate_performed_by_id(self):
        data =  get_user(self.performed_by_id)
        if data:
            return True
        else:
            return False

    def validate_performed_by_org_id(self):
        performed_by_org_data = get_organization(id=self.performed_by_org_id)
        if len(performed_by_org_data) > 0 and performed_by_org_data[0]['account_type'] == 'importer_exporter':
            return True
        else:
            return False
        
    def validate_preferred_customs_rate_currency(self):
        if not self.preferred_customs_rate_currency:
            return True

        fcl_customs_currencies = FCL_CUSTOMS_CURRENCIES

        if self.preferred_customs_rate_currency in fcl_customs_currencies:
            return True
        return False

    def validate_feedback_type(self):
        if self.feedback_type in FEEDBACK_TYPES:
            return True
        return False