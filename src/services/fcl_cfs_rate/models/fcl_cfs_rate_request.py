from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *
from database.rails_db import *
# from micro_services.partner_client import PartnerApiClient
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True
class  FclCfsRateRequest(Model):
    source = CharField()
    source_id = IntegerField(null=True)
    performed_by_id = IntegerField()
    performed_by_org_id = IntegerField()
    port_id = IntegerField()
    closing_remarks = TextField(null=True)
    serial_id = CharField()
    country_id = IntegerField(null=True)
    
    class Meta:
        table_name = 'fcl_cfs_rate_requests'

    def send_closed_notifications_to_sales_agent(self):
        # Implementation here
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

    def send_notifications_to_supply_agents(self):
        # Implementation here
        port = maps.list_locations({'filters':{'id': self.port_id}})['list'][0]['display_name']
        filters = {
            'service_type': 'fcl_cfs',
            'status': 'active',
            'location_id': [self.port_id, self.country_id] if self.country_id else [self.port_id]
        }
        supply_agents_list = partner.list_partner_user_expertises(filters=filters, pagination_data_required=False, page_limit=MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT)['list']
        supply_agents_user_ids = partner.list_partner_usersListPartnerUsers(filters={'id': supply_agents_list}, pagination_data_required=False, page_limit=MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT)['list']
        data = {
            'type': 'platform_notification',
            'service': 'spot_search',
            'service_id': self.source_id,
            'template_name': 'missing_customs_rate_request_notification',
            'variables': {
                'service_type': 'Fcl cfs',
                'location': port
            }
        }
        for user_id in supply_agents_user_ids:
            data['user_id'] = user_id
            common.create_communication(data)