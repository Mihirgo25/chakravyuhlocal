from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from micro_services.client import spot_search, maps
from celery_worker import create_communication_background

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

    def send_closed_notifications_to_sales_agent(self):
        location_data = maps.list_locations({'filters':{'id':str(self.airport_id or '')}})['list']
        if location_data:
            location_pair_name = {location_data[0].get('id'):location_data[0].get('display_name')}
        else:
            location_pair_name = {}
        importer_exporter_data = spot_search.get_spot_search({"id": str(self.source_id)})
        try:
            importer_exporter_id = importer_exporter_data["detail"]["importer_exporter_id"]
        except: 
            importer_exporter_id = None

        data = {
            'user_id': self.performed_by_id,
            'type': 'platform_notification',
            'service': 'air_customs_rate',
            'service_id': self.id,
            'template_name': 'missing_customs_rate_request_completed_notification' if 'rate_added' in self.closing_remarks else 'missing_customs_rate_request_closed_notification',
            'variables': { 'service_type': 'air customs',
                    'location': location_pair_name.get(str(self.airport_id or '')),
                    'remarks':  f"Reason: {self.closing_remarks[0].lower().replace('_', ' ')}." if self.closing_remarks and 'rate_added' in self.closing_remarks else None,
                    'request_serial_id': self.serial_id,
                    'spot_search_id': self.source_id,
                    'importer_exporter_id': importer_exporter_id }
            }
        create_communication_background.apply_async(kwargs = {'data' : self.get_push_notification_data(location_pair_name)}, queue = 'low')
        create_communication_background.apply_async(kwargs = {'data':data}, queue = 'low')

    def get_push_notification_data(self, location_pair_name):
        if 'rate_added' in self.closing_remarks:
            subject = 'Missing Customs Rate Request Completed'
            body = f"Rate has been added for Request No: {self.serial_id}, air customs for {location_pair_name.get(str(self.airport_id or ''))}."
        else:
            subject = 'Missing Customs Rate Request Closed'
            remarks = f"Reason: {self.closing_remarks[0].lower().replace('_', ' ')}."
            body = f"Rate request No: {self.serial_id}, air customs for {location_pair_name.get(str(self.airport_id or ''))} has been closed. {remarks}"

        return {
            'type' : 'push_notification',
            'service': 'air_customs_rate',
            'service_id': self.id,
            'provider_name': 'firebase',
            'template_name': 'push_notification',
            'user_id': self.performed_by_id,
            'variables': {
                'subject' : subject,
                'body' : body,
                'notification_source' : 'spot_search',
                'notification_source_id' : self.source_id
            }
        }