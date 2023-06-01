from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from configs.air_freight_rate_constants import *
from micro_services.client import *
from database.rails_db import *

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateFeedbacks(BaseModel):
    air_freight_rate_id = UUIDField(null=True)
    booking_params = BinaryJSONField(null=True)
    closed_by_id = UUIDField(null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    created_at = DateTimeField()
    feedback_type = CharField(null=True)
    feedbacks = ArrayField(field_class=CharField, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    outcome = CharField(null=True)
    outcome_object_id = UUIDField(null=True)
    performed_by_id = UUIDField(null=True)
    performed_by_org_id = UUIDField(null=True)
    performed_by_type = CharField(null=True)
    preferred_airline_ids = ArrayField(field_class=UUIDField, null=True)
    preferred_airlines=BinaryJSONField(null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    preferred_storage_free_days = IntegerField(null=True)
    remarks = ArrayField(field_class=CharField, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('air_freight_rate_feedback_serial_id_seq'::regclass)")])
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    status = CharField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField()
    validity_id = UUIDField(null=True)
    origin_airport_id:UUIDField(null=True)
    origin_country_id:UUIDField(null=True)
    origin_continent_id  = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    destination_airport_i=UUIDField(null=True)
    destination_continent_id  = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    commodity = CharField(null=True)
    service_provider_id= UUIDField(null=True)
    origin_airport=BinaryJSONField(null=True)
    destination_airport=BinaryJSONField(null=True)
    weight:float(null=True)
    volume:float(null=True)
    packages_count:IntegerField(null=True)

    class Meta:
        table_name = 'air_freight_rate_feedbacks'

    def validate_trade_type(self):
        if self.trade_type not in ['import' , 'export' , 'domestic']:
            raise HTTPException (status_code=400, detail='invalid trade_type')
        
    def validate_feedback_type(self):
        if self.feedback_type not in FEEDBACK_TYPES:
            raise HTTPException(status_code= 400, detail='invalid fedback type')
        
    def validate_preferred_airline_ids(self):
        if not self.preferred_airline_ids:
            return True
        if self.preferred_airline_ids:
            ids = []
            for sl_id in self.preferred_airline_ids:
                ids.append(str(sl_id))
            
            airlines = get_shipping_line(id=ids)
            airlines_hash = {}
            for sl in airlines:
                airlines_hash[sl["id"]] = sl
            for airline_id in self.preferred_airline_ids:
                if not str(airline_id) in airlines_hash:
                    raise HTTPException(status_code=400,detail='invalid airlines')
            self.preferred_airlines = airlines
        return True
    
    def validate_preferred_storage_free_days(self):
        if not  self.preferred_storage_free_days >0.0:
            raise HTTPException(status_code=400, detail='freedays should be greater than zero')
    
    def validate_feedbacks(self):
        for feedback in self.feedbacks:
            if feedback not in POSSIBLE_FEEDBACKS:
                raise HTTPException(status_code=400,detail='invalid feedback type')
            
    def validate_perform_by_org_id(self):
        performed_by_org_data=get_organization(id=self.performed_by_org_id)
        if len(performed_by_org_data) >0 and performed_by_org_data['account_type']=='importer_exporter':
            return True
        else:
            raise HTTPException(status_code=400, detail='invalid org id ')

    def validate_source(self):
        if self.source and self.source not in FEEDBACK_SOURCES:
            raise HTTPException(status_code=400,detail='invalid feedback source')
        
    def validate_source_id(self):
        if self.source =='spot_search':
            spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})
            if 'list' in spot_search_data and len(spot_search_data['list']) != 0:
                return True
        if self.source == 'checkout':
           checkout_data = checkout.list_checkouts({'filters':{'id': [str(self.source_id)]}})
           if 'list' in checkout_data and len(checkout_data['list']) != 0:
               return True
        raise HTTPException(status_code=400, detail='invalid source -id')


    def validate_before_save(self):
        self.validate_trade_type()
        self.validate_feedback_type()
        self.validate_preferred_airline_ids()
        self.validate_preferred_storage_free_days()
        self.validate_feedbacks()
        self.validate_perform_by_org_id()
        self.validate_source()
        return  True
