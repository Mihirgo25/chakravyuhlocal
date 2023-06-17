from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from fastapi import HTTPException
from configs.fcl_customs_rate_constants import REQUEST_SOURCES
from micro_services.client import *
from database.rails_db import *

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCustomsRateRequest(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source = CharField(index=True, null=True)
    source_id = UUIDField(index=True, null=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by_org_id = UUIDField(index=True, null=True)
    performed_by_type = CharField(null=True)
    preferred_customs_rate = DoubleField(null=True)
    preferred_customs_rate_currency = CharField(null=True)
    cargo_readiness_date = DateTimeField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)
    booking_params = BinaryJSONField(null=True)
    status = CharField(index=True, null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)
    closed_by_id = UUIDField(index=True, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_customs_rate_request_serial_id_seq'::regclass)")])
    created_at = DateTimeField(index=True, default = datetime.datetime.now)
    updated_at = DateTimeField(default = datetime.datetime.now)
    containers_count = IntegerField(null=True)
    container_size = CharField(index=True, null=True)
    commodity = CharField(null=True)
    cargo_handling_type = CharField(index=True, null=True)
    country_id = UUIDField(null=True)
    port_id = UUIDField(index=True, null=True)
    container_type = CharField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    performed_by = BinaryJSONField(null=True)
    closed_by = BinaryJSONField(null=True)
    spot_search = BinaryJSONField(null=True)
    port = BinaryJSONField(null=True)

    class Meta:
        table_name = 'fcl_customs_rate_requests'

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCustomsRateRequest, self).save(*args, **kwargs)

    def validate_source_id(self):
        if self.source == 'spot_search':
            spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})['list']
            if len(spot_search_data) == 0:
                raise HTTPException(status_code=400, detail="Invalid Source ID")
            self.spot_search = {key:value for key,value in spot_search_data[0].items() if key in ['id', 'importer_exporter_id', 'importer_exporter', 'service_details']}
    
    def set_port(self):
        port_data = maps.list_locations({'filters':{'id':self.port_id}})['list']
        if port_data:
            self.port = {key:value for key,value in port_data[0].items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}

    def send_closed_notifications_to_sales_agent(self):
        location_pair = FclCustomsRateRequest.select(FclCustomsRateRequest.port_id).where(FclCustomsRateRequest.source_id == self.source_id).limit(1).dicts().get()
        location_pair_data = maps.list_locations({ 'filters': {'id': [str(location_pair['port_id'])] }})['list']
        location_pair_name = {data['id']:data['display_name'] for data in location_pair_data}
        importer_exporter_id = spot_search.get_spot_search({'id': str(self.source_id)})['detail']['importer_exporter_id']

        data = {
            'user_id': self.performed_by_id,
            'type': 'platform_notification',
            'service': 'fcl_customs_rate',
            'service_id': self.id,
            'template_name': 'missing_customs_rate_request_completed_notification' if 'rate_added' in self.closing_remarks else 'missing_customs_rate_request_closed_notification',
            'variables': { 
                'service_type': 'fcl customs',
                'location': location_pair_name[location_pair['port_id']],
                'remarks': None if 'rate_added' in self.closing_remarks else "Reason: {}.".format(self.closing_remarks[0].lower().replace('_', ' ')),
                'request_serial_id': str(self.serial_id),
                'spot_search_id': str(self.source_id),
                'importer_exporter_id': importer_exporter_id 
            }
        }
        common.create_communication(data)
        