from peewee import *
from database.db_session import db
from database.rails_db import get_user
from playhouse.postgres_ext import *
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import REQUEST_SOURCES
import datetime
from configs.global_constants import PROD_DATA_OPERATIONS_ASSOCIATE_ROLE_ID
from micro_services.client import *
from database.rails_db import *
from database.rails_db import get_operators
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.fcl_freight_rate.models.fcl_freight_rate_local import FclFreightRateLocal
from fastapi.encoders import jsonable_encoder
from celery_worker import create_communication_background

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateLocalFeedback(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    fcl_freight_rate_local_id = UUIDField(null=True,index=True)
    feedback_type = CharField(index=True, null=True)
    feedbacks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    booking_params = BinaryJSONField(index=True, null=True)
    cogo_entity_id = UUIDField(index=True,null=True)
    closed_by_id = UUIDField(index=True, null=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = ArrayField(field_class=CharField, null=True)
    commodity = CharField(null=True)
    container_size=CharField(null=True)
    container_type=CharField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(index=True, null=True)
    created_at = DateTimeField(index=True, default=datetime.datetime.now)
    main_port_id = UUIDField(null=True)
    main_port = BinaryJSONField(null=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by = BinaryJSONField(null=True)
    performed_by_org_id = UUIDField(null=True)
    performed_by_org = BinaryJSONField(null=True)
    performed_by_type = CharField(null=True)
    port_id = UUIDField(index=True, null=True)
    port = BinaryJSONField(null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    remarks = ArrayField(field_class=CharField, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_local_feedback_serial_id_seq'::regclass)")])
    shipping_line_id = UUIDField(null=True)
    source = CharField(null=True)
    source_id = UUIDField(index=True, null=True)
    status = CharField(index=True, null=True)
    trade_id = UUIDField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    service_provider_id= UUIDField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    spot_search_serial_id = BigIntegerField(null = True)
    attachment_file_urls = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)

    class Meta:
        table_name = "fcl_freight_rate_local_feedbacks"

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateLocalFeedback, self).save(*args, **kwargs)
    
    def supply_agents_to_notify(self, request):
        locations_data = FclFreightRateLocalFeedback.select(FclFreightRateLocalFeedback.port_id, FclFreightRateLocalFeedback.country_id, FclFreightRateLocalFeedback.continent_id).where(FclFreightRateLocalFeedback.source_id == request.get('source_id')).dicts().get()
        locations = list(filter(None,[str(value or "") for key,value in locations_data.items()]))

        supply_agents_data = get_partner_users_by_expertise('fcl_freight_local', location_ids = locations, trade_type = request.get('trade_type'))
        supply_agents_list = list(set([item.get('partner_user_id') for item in supply_agents_data]))

        supply_agents_user_data = get_partner_users(supply_agents_list)
        supply_agents_user_ids = list(set([str(data['user_id']) for data in  supply_agents_user_data])) if supply_agents_user_data else None

        port_ids = str(locations_data.get('port_id') or '')

        route_data = []
        try:
            route_data = maps.list_locations({'filters':{'id':port_ids}})['list']
        except Exception as e:
            print(e)

        route = {key['id']:key['display_name'] for key in route_data}
        return { 'user_ids': supply_agents_user_ids, 'location': route.get(str(locations_data.get('port_id') or '')) }

    def send_notifications_to_supply_agents(self, request):
        request_info = self.supply_agents_to_notify(request)
        data = {
            'type': 'platform_notification',
            'service': 'spot_search',
            'service_id': request.get('source_id'),
            'template_name': 'local_rate_disliked',
            'variables': { 
                'service_type': 'fcl freight local',
                'location': request_info.get('location'),
                'details':request.get('booking_params')
            }
        }
        for user_id in (request_info.get('user_ids') or []):
            data['user_id'] = user_id
            create_communication_background.apply_async(kwargs = {'data':data}, queue = 'low')

    def send_closed_notifications_to_sales_agent(self):
        locations_data_query = FclFreightRateLocal.select(
            FclFreightRateLocal.port_id
        ).where(FclFreightRateLocal.id == self.fcl_freight_rate_local_id)
        locations_data = jsonable_encoder(list(locations_data_query.dicts()))

        if locations_data:
            locations_data = locations_data[0]

            locations = locations_data.get('port_id')
            location_name = maps.list_locations({'filters':{ 'id':locations }})['list']
            if location_name:
                location_name = location_name[0].get('display_name')
            else:
                location_name = None

            importer_exporter_id = spot_search.get_spot_search({'id':str(self.source_id)})['detail']['importer_exporter_id']
            data = {
                "user_id": str(self.performed_by_id or ''),
                "type": "platform_notification",
                "service": "fcl_freight_local",
                "service_id": str(self.id),
                "template_name": "local_rate_feedback_completed_notification" if ("rate_added" in self.closing_remarks) else "local_rate_feedback_closed_notification",
                "variables": {
                    "service_type": "fcl freight local",
                    "location": location_name,
                    "remarks": None
                    if ("rate_added" in self.closing_remarks)
                    else f"Reason: {self.closing_remarks[0].lower().replace('_', ' ')}",
                    "request_serial_id": str(self.serial_id or ''),
                    "spot_search_id": str(self.source_id or ''),
                    "importer_exporter_id": importer_exporter_id
                }
            }
            common.create_communication(data)