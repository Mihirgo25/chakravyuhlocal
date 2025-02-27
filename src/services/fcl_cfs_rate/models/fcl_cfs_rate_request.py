from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *
from database.rails_db import *
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
import datetime
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import RATE_FEEDBACK_RELEVANT_ROLE_ID


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True
class FclCfsRateRequest(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True, index=True)
    port_id	= UUIDField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_cfs_rate_request_serial_id_seq'::regclass)")])
    country_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    container_size = CharField(null=True)
    container_type = CharField(null=True)
    commodity = CharField(null=True)
    status = CharField(null=True)
    preferred_rate = FloatField(null=True)
    preferred_rate_currency	= CharField(null=True)
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    performed_by_id = UUIDField(null=True)
    performed_by_type = CharField(null=True)
    performed_by_org_id = UUIDField(null=True)
    closed_by_id = UUIDField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    booking_params = BinaryJSONField(null=True)
    preferred_detention_free_days = IntegerField(null = True)
    cargo_readiness_date = DateField(null=True)	
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    port = BinaryJSONField(null=True)
    performed_by = BinaryJSONField(null=True)
    closed_by = BinaryJSONField(null=True)
    spot_search = BinaryJSONField(null=True)


    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCfsRateRequest, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_cfs_rate_requests'  
    
    def send_closed_notifications_to_sales_agent(self):
        
        port = maps.list_locations({'filters':{'id': self.port_id}})['list'][0]['display_name']
        try:
            importer_exporter_id = spot_search.get_spot_search({'id': str(self.source_id)})['detail']['importer_exporter_id']
        except:
            importer_exporter_id = None
        closing_remarks = self.closing_remarks or []
        template_name = 'missing_cfs_rate_request_completed_notification' if 'rate_added' in closing_remarks else 'missing_cfs_rate_request_closed_notification'
        remarks = None if 'rate_added' in closing_remarks else f"Reason: {closing_remarks[0].lower().replace('_', ' ')}."
        data = {
            'user_id': self.performed_by_id,
            'type': 'platform_notification',
            'service': 'fcl_cfs_rate_request',
            'service_id': self.id,
            'template_name': template_name,
            'variables': {
                'service_type': 'Fcl cfs',
                'origin_location': port,
                'remarks': remarks,
                'request_serial_id': self.serial_id,
                'spot_search_id': self.source_id,
                'importer_exporter_id': importer_exporter_id
            }
        }
        common.create_communication(data)
    def set_port(self):
        port_data = maps.list_locations({'filters':{'id':self.port_id}})['list']

        if port_data:
            self.port = {key:value for key,value in port_data[0].items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}
            
    def set_spot_search(self):
        spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})['list']
        self.spot_search = {key:value for key,value in spot_search_data[0].items() if key in ['id', 'importer_exporter_id', 'importer_exporter', 'service_details']}

    def send_notifications_to_supply_agents(self):
        port = maps.list_locations({'filters':{'id': self.port_id}})['list']
        filters = {
            'service_type': 'fcl_cfs',
            'status': 'active',
            'location_id': [self.port_id, self.country_id] if self.country_id else [self.port_id]
        }

        supply_agents_data = get_partner_users_by_expertise(service = filters['service_type'],location_ids = filters['location_id'], trade_type = self.trade_type)
        supply_agents_list = list(set([item['partner_user_id'] for item in supply_agents_data]))
        supply_agents_user_data = get_partner_users(ids = supply_agents_list, role_ids = list(RATE_FEEDBACK_RELEVANT_ROLE_ID.values()))

        if supply_agents_user_data:
            supply_agents_user_ids = list(set([str(data['user_id']) for data in supply_agents_user_data]))
        else:
            supply_agents_user_ids = []

        data = {
            'type': 'platform_notification',
            'service': 'spot_search',
            'service_id': self.source_id,
            'template_name': 'missing_customs_rate_request_notification',
            'variables': {
                'service_type': 'Fcl cfs',
                'location': port[0]['display_name']
            }
        }
        for user_id in supply_agents_user_ids:
            data['user_id'] = user_id
            common.create_communication(data)