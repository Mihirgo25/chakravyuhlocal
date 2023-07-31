from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
import datetime
from micro_services.client import *
from database.rails_db import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FtlFreightRateRequest(BaseModel):
    booking_params = BinaryJSONField(null=True)
    cogo_entity_id = UUIDField(index=True, null = True)
    closed_by_id = UUIDField(index=True, null=True)
    closed_by = BinaryJSONField(null=True)
    cargo_readiness_date = DateTimeField(null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    commodity = CharField(index=True, null=True)
    created_at = DateTimeField(index=True, default = datetime.datetime.now)
    destination_country_id = UUIDField( null=True)
    destination_cluster_id = UUIDField( null=True)
    destination_location_id = UUIDField(index=True)
    destination_location = BinaryJSONField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_country_id = UUIDField( null=True)
    origin_location_id = UUIDField(index=True, null=True)
    origin_location = BinaryJSONField(null=True)
    origin_city_id = UUIDField( null=True)
    origin_cluster_id = UUIDField(null=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by = BinaryJSONField(null=True)
    performed_by_org_id = UUIDField(index=True, null=True)
    performed_by_type = CharField(index=True, null=True)
    preferred_detention_free_days = IntegerField(null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    preferred_storage_free_days = IntegerField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    request_type = TextField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('ftl_freight_rate_request_serial_id_seq'::regclass)")])
    source = CharField( null=True)
    source_id = UUIDField(index=True ,null=True)
    status = CharField(index=True, null=True)
    updated_at = DateTimeField(default = datetime.datetime.now)
    reverted_rates_count = IntegerField(null=True)
    reverted_by_user_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    trip_type = TextField(null=True)
    trucks_count = IntegerField(null=True)
    truck_type = TextField(null=True)
    destination_city_id = UUIDField(null= True)
    packages = BinaryJSONField(null=True)
    free_detention_hours = IntegerField(null= True)
    load_selection_type = TextField(null= True)
    trade_type = TextField(null=True)
    relevant_supply_agent_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)


    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FtlFreightRateRequest, self).save(*args, **kwargs)

    class Meta:
        table_name = 'ftl_freight_rate_requests'

    def set_location(self):
        location_data = maps.list_locations({'filters':{'id':[self.origin_location_id,self.destination_location_id]}})['list']
        for location in location_data:
            if location['id']==self.origin_location_id:
                self.origin_location = {key:value for key,value in location.items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}
            elif location['id']==self.destination_location_id:
                self.destination_location = {key:value for key,value in location.items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}


    def send_closed_notifications_to_sales_agent(self):
        location_pair = FtlFreightRateRequest.select(FtlFreightRateRequest.origin_location_id, FtlFreightRateRequest.destination_location_id).where(FtlFreightRateRequest.source_id == self.source_id).limit(1).dicts().get()
        location_pair_data = maps.list_locations({ 'filters': {'id': [str(location_pair['origin_location_id']), str(location_pair['destination_location_id'])] }})['list']
        location_pair_name = {data['id']:data['display_name'] for data in location_pair_data}
        try:
            importer_exporter_id = spot_search.get_spot_search({'id': str(self.source_id)})['detail']['importer_exporter_id']
        except:
            importer_exporter_id = None
        origin_location = location_pair_name[str(location_pair['origin_location_id'])]
        destination_location = location_pair_name[str(location_pair['destination_location_id'])]
        data = {
            'user_id': self.performed_by_id,
            'type': 'platform_notification',
            'service': 'ftl_freight_rate',
            'service_id': self.id,
            'template_name': 'freight_rate_request_completed_notification' if 'rate_added' in self.closing_remarks else 'freight_rate_request_closed_notification',
            'variables': {
                'service_type': 'ftl freight',
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
            body = f"Rate has been added for Request No: {str(self.serial_id)}, ftl freight from {origin_location} to {destination_location}."
        else:
            subject = 'Freight Rate Request Closed'
            remarks = f"Reason: {self.closing_remarks[0].lower().replace('_', ' ')}."
            body = f"Your rate request has been closed for Request No: {str(self.serial_id)}, ftl freight from {origin_location} to {destination_location}. {remarks}"

        push_notification_data = {
        'type': 'push_notification',
        'service': 'ftl_freight_rate',
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

        common.create_communication(push_notification_data)
        common.create_communication(data)
