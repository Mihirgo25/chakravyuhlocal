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

class FclCfsRateFeedback(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source = CharField(index=True, null=True)
    source_id = UUIDField(null=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by_org_id = UUIDField(null=True)
    performed_by_type = CharField(index=True, null=True)
    preferred_rate = DoubleField(null=True)
    preferred_rate_currency = CharField(null=True)
    feedbacks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    fcl_cfs_rate_id = UUIDField(null=True,index=True)
    booking_params = BinaryJSONField(null=True)
    feedback_type = CharField(index=True, null=True)
    status = CharField(index=True, null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    closed_by_id = UUIDField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_cfs_rate_feedback_serial_id_seq'::regclass)")])
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    performed_by = BinaryJSONField(null=True)
    port = BinaryJSONField(null=True)
    closed_by = BinaryJSONField(null=True)
    # organization = BinaryJSONField(null=True)
    service_provider = BinaryJSONField(null=True)
    port_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    trade_id = UUIDField(null=True)
    commodity = CharField(null=True, index=True)
    service_provider_id = UUIDField(null=True)
    reverted_rate = BinaryJSONField(null = True)
    spot_search_serial_id = BigIntegerField(null = True)
    cogo_entity_id = UUIDField(null=True)
    attachment_file_urls = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCfsRateFeedback, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_cfs_rate_feedback'  

    def send_closed_notifications_to_sales_agent(self):
        port = maps.list_locations({'filters':{'id': str(self.port_id or '')}})['list'][0]['display_name']
        try:
            importer_exporter_id = spot_search.get_spot_search({'id': str(self.source_id)})['detail']['importer_exporter_id']
        except:
            importer_exporter_id = None
        closing_remarks = self.closing_remarks or []
        template_name = 'customs_rate_feedback_completed_notification' if 'rate_added' in closing_remarks else 'customs_rate_feedback_closed_notification'
        remarks = None if 'rate_added' in closing_remarks else f"Reason: {closing_remarks[0].lower().replace('_', ' ')}."
        data = {
            'user_id': str(self.performed_by_id),
            'type': 'platform_notification',
            'service': 'fcl_cfs',
            'service_id': str(self.id),
            'template_name': template_name,
            'variables': {
                'service_type': 'Fcl cfs',
                'location': port,
                'remarks': remarks,
                'feedback_serial_id': str(self.serial_id or ''),
                'spot_search_id': str(self.source_id or ''),
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

    def send_notifications_to_supply_agents(self, request):
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
            'template_name': 'customs_rate_disliked',
            'variables': {
                'service_type': 'Fcl cfs',
                'location': port[0]['display_name'],
                'details': request.get('booking_params')
            }
        }
        for user_id in supply_agents_user_ids:
            data['user_id'] = user_id
            common.create_communication(data)