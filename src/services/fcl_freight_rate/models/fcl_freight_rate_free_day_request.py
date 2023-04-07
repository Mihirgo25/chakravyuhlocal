from peewee import *
from configs.fcl_freight_rate_constants import REQUEST_SOURCES
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from micro_services.client import *
from database.rails_db import *
from micro_services.client import common

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateFreeDayRequest(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    location_id = UUIDField(index=True, null=True)
    location = BinaryJSONField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_free_day_request_serial_id_seq'::regclass)")])
    country_id = UUIDField(index=True, null = True)
    trade_id = UUIDField(null=True)
    continent_id = UUIDField(null = True)
    main_port_id = UUIDField(null=True)
    trade_type = CharField(index=True, null=True)
    commodity = CharField(null=True)
    status = CharField(index=True, null=True)
    free_days_type = CharField(index=True, null=True)
    preferred_free_days = CharField(null=True)
    shipping_line_id = UUIDField(null=True)
    shipping_line = BinaryJSONField(null=True)
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)
    source = CharField(index=True, null=True)
    source_id = UUIDField(index=True, null = True)
    performed_by_id = UUIDField(index=True, null = True)
    performed_by = BinaryJSONField(null=True)
    performed_by_type = CharField(index=True, null=True)
    performed_by_org_id = UUIDField(index=True, null = True)
    closed_by_id = UUIDField(index=True, null = True)
    closed_by = BinaryJSONField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    booking_params = BinaryJSONField(null=True)
    cargo_readiness_date = DateField(null=True)
    cargo_weight_per_container = IntegerField(null=True)
    containers_count = IntegerField(null=True)
    container_size = CharField(index=True, null=True)
    container_type = CharField(index=True, null=True)
    inco_term = CharField(null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    created_at = DateTimeField(index=True, default = datetime.datetime.now)
    updated_at = DateTimeField(default = datetime.datetime.now)
    code = CharField(null=True)
    preferred_total_days = IntegerField(null=True)
    specificity_type = CharField(null=True)

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateFreeDayRequest, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_free_day_requests'

    def send_closed_notifications_to_sales_agent(self):
      locations_data = maps.list_locations({'filters' : {'id': self.location_id}})['list']
      location_name = {data['id']:data['display_name'] for data in locations_data}
      importer_exporter_id = common.get_spot_search({'filters':{'id': self.source_id}})['detail']['importer_exporter_id']
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
      common.create_communication(data)

    def validate_source(self):
      if self.source in REQUEST_SOURCES:
        return True
      return False

    def set_location(self):
      self.location = {key:value for key, value in maps.list_locations({'filters' : {'id': self.location_id}})['list'] if key in ['id', 'name', 'display_name', 'port_code', 'type']}

    # def validate_source_id(self):
    #   data = common.list_spot_searches({'filters':{'id':self.source_id}})
    #   if ('list' in data) and (len(data['list']) > 0):
    #     data = data['list'][0]
    #     if data.get('source_type',None) == 'spot_search':
    #       return True
    #   return False

    def validate_performed_by(self):
        data = get_user(self.performed_by_id)
        if (len(data) > 0):
          return True
        return False

    def validate_performed_by_org(self):
      data = get_organization(id=self.performed_by_id)
      if (len(data) > 0):
          data = data[0]
          if data.get('account_type',None) == 'importer_exporter':
              return True
      return False

    def validate_shipping_line_id(self):
      if not self.shipping_line_id:
        return True

      data = get_shipping_line(id=self.shipping_line_id)
      if len(data) > 0:
        data = data[0]
        if data.get('account_type',None) == 'shipping_line':
          return True
      return False
