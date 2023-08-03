from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
import datetime
from micro_services.client import *
from database.rails_db import *
from configs.haulage_freight_rate_constants import REQUEST_SOURCES

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class HaulageFreightRateRequest(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source = TextField(null=True)
    source_id = UUIDField(index=True ,null=True)
    performed_by_id = UUIDField(null=True)
    performed_by_org_id = UUIDField( null=True)
    performed_by_type = TextField( null=True)
    request_type = TextField(null=True)
    status = TextField(index=True, null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = TextField(null=True)
    preferred_detention_free_days = IntegerField(null=True)
    booking_params = BinaryJSONField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    cargo_readiness_date = DateTimeTZField(null=True)
    closed_by_id = UUIDField(index=True, null=True)
    cargo_weight_per_container = IntegerField(null=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    commodity = TextField(index=True, null=True)
    container_size = TextField(index=True, null=True)
    container_type = TextField(index=True, null=True)
    containers_count = IntegerField(null=True)
    created_at = DateTimeField(index=True, default = datetime.datetime.now)
    destination_city_id = UUIDField( null=True)
    destination_country_id = UUIDField( null=True)
    destination_location_id = UUIDField(index=True, null=True)
    destination_location = BinaryJSONField(null=True)
    destination_cluster_id = UUIDField( null=True)
    origin_city_id = UUIDField( null=True)
    origin_country_id = UUIDField( null=True)
    origin_location_id = UUIDField(index=True, null=True)
    origin_location = BinaryJSONField(null=True)
    origin_cluster_id = UUIDField( null=True)
    performed_by = BinaryJSONField(null=True)
    preferred_shipping_line_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    preferred_shipping_lines = BinaryJSONField(null=True)
    request_type = TextField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('haulage_freight_rate_request_serial_id_seq'::regclass)")])
    updated_at = DateTimeField(default = datetime.datetime.now)
    reverted_rates_count = IntegerField(null=True)
    reverted_by_user_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    expiration_time = DateTimeTZField(null = True)
    trade_type = TextField(index=True, null=True)
    reverted_rate_id = UUIDField(null=True)
    reverted_rate = BinaryJSONField(null=True)
    transport_mode = TextField(index=True)


    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(HaulageFreightRateRequest, self).save(*args, **kwargs)

    class Meta:
        table_name = 'haulage_freight_rate_requests'
        
    
    def send_closed_notifications_to_sales_agent(self):
        location_pair = HaulageFreightRateRequest.select(HaulageFreightRateRequest.origin_location_id, HaulageFreightRateRequest.destination_location_id).where(HaulageFreightRateRequest.source_id == self.source_id).limit(1).dicts().get()
        location_pair_data = maps.list_locations({ 'filters': {'id': [str(location_pair['origin_location_id']), str(location_pair['destination_location_id'])] }})['list']
        location_pair_name = {data['id']:data['display_name'] for data in location_pair_data}
        try:
            importer_exporter_id = spot_search.get_spot_search(
                {"id": str(self.source_id)}
            )["detail"]["importer_exporter_id"]
        except:
            importer_exporter_id = None

        origin_location = location_pair_name[str(location_pair['origin_location_id'])]
        destination_location = location_pair_name[str(location_pair['destination_location_id'])]
        if not self.closing_remarks:
            self.closing_remarks = ' '
        data = {
            'user_id': self.performed_by_id,
            'type': 'platform_notification',
            'service': 'haulage_freight_rate',
            'service_id': self.id,
            'template_name': 'freight_rate_request_completed_notification' if 'rate_added' in self.closing_remarks else 'freight_rate_request_closed_notification',
            'variables': {
                'service_type': 'haulage freight',
                'origin_location': origin_location,
                'destination_location': destination_location,
                'remarks': None if 'rate_added' in self.closing_remarks else "Reason: {}.".format(self.closing_remarks[0].lower().replace('_', ' ')),
                'request_serial_id': str(self.serial_id),
                'spot_search_id': str(self.source_id),
                'importer_exporter_id': importer_exporter_id 
            }
        }

        if 'rate_added' in self.closing_remarks:
            subject = 'Freight Rate Request Completed'
            body = f"Rate has been added for Request No: {str(self.serial_id)}, haulage freight from {origin_location} to {destination_location}."
        else:
            subject = 'Freight Rate Request Closed'
            remarks = f"Reason: {self.closing_remarks[0].lower().replace('_', ' ')}."
            body = f"Your rate request has been closed for Request No: {str(self.serial_id)}, haulage freight from {origin_location} to {destination_location}. {remarks}"

        push_notification_data = {
        'type': 'push_notification',
        'service': 'haulage_freight_rate',
        'service_id': str(self.id),
        'provider_name': 'firebase',
        'template_name': 'push_notification',
        'user_id': str(self.performed_by_id),
        'variables': {
            'subject': subject,
            'body': body,
            'notification_source': 'spot_search',
            'notification_source_id': str(self.source_id)
            }
        }
        common.create_communication(data)
        common.create_communication(push_notification_data)
