from peewee import *
from configs.fcl_freight_rate_constants import REQUEST_SOURCES
from database.db_session import db
from playhouse.postgres_ext import *
from rails_client import client
import datetime

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateFreeDayRequest(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    location_id = UUIDField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_free_day_requests_serial_id_seq'::regclass)")])
    country_id = UUIDField(null = True)
    trade_id = UUIDField(null=True)
    continent_id = UUIDField(null = True)
    main_port_id = UUIDField(null=True) 
    trade_type = CharField(null=True)
    commodity = CharField(null=True)
    status = CharField(null=True)
    free_days_type = CharField(null=True)
    preferred_free_days = CharField(null=True)
    shipping_line_id = UUIDField(null=True)
    service_provider_id = UUIDField(null=True)
    source = CharField(null=True)
    source_id = UUIDField(null = True)
    performed_by_id = UUIDField(null = True)
    performed_by_type = CharField(null=True)
    performed_by_org_id = UUIDField(null = True)
    closed_by_id = UUIDField(null = True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    booking_params = BinaryJSONField(null=True)
    cargo_readiness_date = DateField(null=True)
    cargo_weight_per_container = IntegerField(null=True)
    containers_count = IntegerField(null=True)
    container_size = CharField(null=True)
    container_type = CharField(null=True)
    inco_term = CharField(null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    created_at = DateTimeField(default = datetime.datetime.now)   
    updated_at = DateTimeField(default = datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateFreeDayRequest, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_free_day_requests'

    def send_closed_notifications_to_sales_agent(self):
      locations_data = client.ruby.list_locations({'filters': {'id': self.location_id}})['list']
      location_name = {data['id']:data['display_name'] for data in locations_data}
      importer_exporter_id = client.ruby.get_spot_search({'id': self.source_id})['detail']['importer_exporter_id']
      data = {
        'user_id': self.performed_by_id,
        'type': 'platform_notification',
        'service':  'fcl_freight_rate_free_day_request',
        'service_id': self.id,
        'template_name': 'missing_fcl_freight_rate_free_day_request_completed_notification',
        'variables': { 
          'service_type': self.free_days_type,
          'location': location_name[self.location_id],
          'remarks': 'Reason: Request fulfilled' if 'rate_added' in self.closing_remarks else "Reason: {}.".format(', '.join([t.lower().replace('_', ' ') for t in self.closing_remarks])),
          'request_serial_id': self.serial_id,
          'spot_search_id': self.source_id,
          'importer_exporter_id': importer_exporter_id }
      }
      client.ruby.create_communication(data)

    def validate_source(self):
      if self.source in REQUEST_SOURCES:
        return True
      return False
    
    
    def validate_source_id(self):
      data = client.ruby.list_spot_searches({'filters':{'id':self.source_id}})
      if ('list' in data) and (len(data['list']) > 0):
        data = data['list'][0]
        if data.get('source_type',None) == 'spot_search':
          return True
      return False
      
    def validate_performed_by(self):
        data = client.ruby.list_users({'filters':{'id': self.performed_by_id}})
        if ('list' in data) and (len(data['list']) > 0):
          return True
        return False

    def validate_performed_by_org(self):
      data = client.ruby.list_organizations({'filters':{'id': self.performed_by_id}})
      if ('list' in data) and (len(data['list']) > 0):
          data = data['list'][0]
          if data.get('account_type',None) == 'importer_exporter':
              return True
      return False

    def validate_shipping_line_id(self):
      if not self.shipping_line_id:
        return True
        
      data = client.ruby.list_organizations({'filters':{'id': self.shipping_line_id}})
      if ('list' in data) and (len(data['list']) > 0):
        data = data['list'][0]
        if data.get('account_type',None) == 'shipping_line':
          return True
      return False