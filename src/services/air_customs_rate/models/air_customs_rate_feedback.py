from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from micro_services.client import spot_search, maps, common
from services.air_customs_rate.models.air_customs_rate import AirCustomsRate
from fastapi.encoders import jsonable_encoder

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirCustomsRateFeedback(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    source = CharField(index=True, null=True)
    source_id = UUIDField(null=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by_org_id = UUIDField(null=True)
    performed_by_type = CharField(index=True, null=True)
    preferred_customs_rate = DoubleField(null=True)
    preferred_customs_rate_currency = CharField(null=True)
    feedbacks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    air_customs_rate_id = UUIDField(null=True,index=True)
    booking_params = BinaryJSONField(null=True)
    feedback_type = CharField(index=True, null=True)
    status = CharField(index=True, null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    closed_by_id = UUIDField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('air_customs_rate_feedback_serial_id_seq'::regclass)")])
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    performed_by = BinaryJSONField(null=True)
    airport = BinaryJSONField(null=True)
    closed_by = BinaryJSONField(null=True)
    organization = BinaryJSONField(null=True)
    spot_search = BinaryJSONField(null=True)
    service_provider = BinaryJSONField(null=True)
    airport_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    commodity = CharField(null=True, index=True)
    service_provider_id = UUIDField(null=True)
    continent_id = UUIDField(null=True)
    city_id = UUIDField(null=True)
    reverted_rate = BinaryJSONField(null = True)
    spot_search_serial_id = BigIntegerField(index=True, null = True)
    attachment_file_urls = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirCustomsRateFeedback, self).save(*args, **kwargs)

    class Meta:
        table_name = 'air_customs_rate_feedbacks'

    def set_airport(self):
        airport_data = maps.list_locations({'filters':{'id':str(self.airport_id)}})['list']
        if airport_data:
            self.airport = {key:value for key,value in airport_data[0].items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}

    def set_spot_search(self):
        spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})['list']
        self.spot_search = {key:value for key,value in spot_search_data[0].items() if key in ['id', 'importer_exporter_id', 'importer_exporter', 'service_details']}

    def send_closed_notifications_to_sales_agent(self):
        locations_data_query = AirCustomsRate.select(
            AirCustomsRate.airport_id
        ).where(AirCustomsRate.id == self.air_customs_rate_id)
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
                "user_id": str(self.performed_by_id),
                "type": "platform_notification",
                "service": "air_customs_rate",
                "service_id": str(self.id),
                "template_name": "customs_rate_feedback_completed_notification" if ("rate_added" in self.closing_remarks) else "customs_rate_feedback_closed_notification",
                "variables": {
                    "service_type": "air customs",
                    "location": location_name,
                    "remarks": None
                    if ("rate_added" in self.closing_remarks)
                    else f"Reason: {self.closing_remarks[0].lower().replace('_', ' ')}",
                    "request_serial_id": str(self.serial_id or ''),
                    "spot_search_id": str(self.source_id or ''),
                    "importer_exporter_id": importer_exporter_id
                },
            }
            common.create_communication(data)