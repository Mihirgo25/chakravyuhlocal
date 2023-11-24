from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from services.air_freight_rate.constants.air_freight_rate_constants import *
from micro_services.client import *
from database.rails_db import *
from services.air_freight_rate.models.air_freight_rate_local import AirFreightRateLocal
from celery_worker import create_communication_background
import datetime
from fastapi.encoders import jsonable_encoder

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateLocalFeedback(BaseModel):
    air_freight_rate_local_id = UUIDField(null=True,index=True)
    booking_params = BinaryJSONField(null=True)
    closed_by_id = UUIDField(null=True,index=True)
    closing_remarks = ArrayField(
        constraints=[SQL("DEFAULT '{}'::character varying[]")],
        field_class=TextField,
        null=True,
    )
    created_at = DateTimeField(default=datetime.datetime.now)
    feedback_type = CharField(null=True)
    feedbacks = ArrayField(field_class=TextField, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    performed_by_id = UUIDField(null=True,index=True)
    performed_by = BinaryJSONField(null=True)
    performed_by_org_id = UUIDField(null=True,index=True)
    performed_by_org = BinaryJSONField(null=True)
    performed_by_type = CharField(null=True)
    preferred_rate = DoubleField(null=True)
    preferred_rate_currency = CharField(null=True)
    remarks = ArrayField(field_class=TextField, null=True)
    serial_id = BigIntegerField(
        constraints=[
            SQL("DEFAULT nextval('air_freight_rate_local_feedback_serial_id_seq'::regclass)")
        ]
    )
    source = CharField(null=True)
    source_id = UUIDField(null=True,index=True)
    status = CharField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    closed_by = BinaryJSONField(null=True)
    reverted_rate = BinaryJSONField(null=True)
    airport_id = UUIDField(null=True, index=True)
    country_id = UUIDField(null=True, index=True)
    continent_id = UUIDField(null=True, index=True)
    trade_id = UUIDField(null=True, index=True)
    cogo_entity_id = UUIDField(null=True, index=True)
    service_provider_id = UUIDField(null=True, index=True)
    commodity = TextField(null=True,index=True)
    airline_id=UUIDField(null=True,index=True)
    spot_search_serial_id = BigIntegerField(index = True, null = True)
    attachment_file_urls = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    airline = BinaryJSONField(null = True)

    class Meta:
        table_name = "air_freight_rate_local_feedbacks"
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(AirFreightRateLocalFeedback, self).save(*args, **kwargs)
    
    def supply_agents_to_notify(self):
        locations_data = AirFreightRateLocalFeedback.select(AirFreightRateLocalFeedback.airport_id, AirFreightRateLocalFeedback.country_id, AirFreightRateLocalFeedback.continent_id).where(AirFreightRateLocalFeedback.source_id == self.source_id).dicts().get()
        locations = list(filter(None,[str(value or "") for key,value in locations_data.items()]))

        supply_agents_data = get_partner_users_by_expertise('air_freight_local', location_ids = locations, trade_type = self.trade_type)
        supply_agents_list = list(set([item.get('partner_user_id') for item in supply_agents_data]))

        supply_agents_user_data = get_partner_users(supply_agents_list)
        supply_agents_user_ids = list(set([str(data['user_id']) for data in  supply_agents_user_data])) if supply_agents_user_data else None

        airport_ids = str(locations_data.get('airport_id') or '')

        route_data = []
        try:
            route_data = maps.list_locations({'filters':{'id':airport_ids}})['list']
        except Exception as e:
            print(e)

        route = {key['id']:key['display_name'] for key in route_data}
        return { 'user_ids': supply_agents_user_ids, 'location': route.get(str(locations_data.get('airport_id') or '')) }

    def send_notifications_to_supply_agents(self):
        request_info = self.supply_agents_to_notify()
        data = {
            'type': 'platform_notification',
            'service': 'spot_search',
            'service_id': self.source_id,
            'template_name': 'local_rate_disliked',
            'variables': { 
                'service_type': 'air freight local',
                'location': request_info.get('location'),
                'details':self.booking_params
            }
        }
        for user_id in (request_info.get('user_ids') or []):
            data['user_id'] = user_id
            create_communication_background.apply_async(kwargs = {'data':data}, queue = 'low')

    def send_closed_notifications_to_sales_agent(self):
        locations_data_query = AirFreightRateLocal.select(
            AirFreightRateLocal.airport_id
        ).where(AirFreightRateLocal.id == self.air_freight_rate_local_id)
        locations_data = jsonable_encoder(list(locations_data_query.dicts()))

        if locations_data:
            locations_data = locations_data[0]

            locations = locations_data.get('airport_id')
            location_name = maps.list_locations({'filters':{ 'id':locations }})['list']
            if location_name:
                location_name = location_name[0].get('display_name')
            else:
                location_name = None

            importer_exporter_id = spot_search.get_spot_search({'id':str(self.source_id)})['detail']['importer_exporter_id']
            data = {
                "user_id": str(self.performed_by_id or ''),
                "type": "platform_notification",
                "service": "air_freight_local",
                "service_id": str(self.id),
                "template_name": "local_rate_feedback_completed_notification" if ("rate_added" in self.closing_remarks) else "local_rate_feedback_closed_notification",
                "variables": {
                    "service_type": "air freight local",
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

    def set_airline(self):
        if self.airline or not self.airline_id:
            return
        airline = get_operators(id=self.airline_id, operator_type="airline")
        if len(airline) != 0:
            self.airline = {
                key: str(value)
                for key, value in airline[0].items()
                if key in ["id", "business_name", "short_name", "logo_url"]
            }