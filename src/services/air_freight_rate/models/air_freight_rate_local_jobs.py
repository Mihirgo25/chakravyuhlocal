from peewee import *
import datetime
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *
from database.rails_db import *


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class AirFreightRateLocalJob(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    airport = BinaryJSONField(null=True)
    airport_id = UUIDField(null=True, index=True)
    service_provider = BinaryJSONField(null=True)
    service_provider_id = UUIDField(null=True, index=True)
    importer_exporter = BinaryJSONField(null=True)
    importer_exporter_id = UUIDField(null=True, index=True)
    airline = BinaryJSONField(null=True)
    airline_id = UUIDField(null=True, index=True)
    commodity = CharField(null=True, index=True)
    commodity_type = CharField(null=True, index=True)
    commodity_sub_type = CharField(null=True)
    trade_type = CharField(null=True, index=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    status = CharField(index=True, null=True)
    sources = ArrayField(
        constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True
    )
    user_id = UUIDField(index=True, null=True)
    assigned_to = BinaryJSONField(null=True)
    closed_by_id = UUIDField(null=True, index=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = TextField(null=True)
    shipment_type = CharField(null=True)
    rate_type = TextField(null=True)
    init_key = TextField(index=True, null=True)
    operation_type = CharField(null=True)
    price_type = CharField(null=True)
    cogo_entity_id = UUIDField(null=True, index=True)
    serial_id = BigIntegerField(
        constraints=[SQL("DEFAULT nextval('air_freight_rate_local_jobs_serial_id_seq')")],
    )

    class Meta:
        table_name = "air_freight_rate_local_jobs"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirFreightRateLocalJob, self).save(*args, **kwargs)

    def set_locations(self):
        ids = []
        if self.airport_id:
            ids.append(str(self.airport_id))

        obj = {"filters": {"id": ids, "type": "airport"}}
        locations_response = maps.list_locations(obj)
        locations = []
        if "list" in locations_response:
            locations = locations_response["list"]
        for location in locations:
            if str(self.airport_id) == str(location["id"]):
                self.airport = self.get_required_location_data(location)

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

    def get_required_location_data(self, location):
        loc_data = {
            "id": location["id"],
            "name": location["name"],
            "display_name": location["display_name"],
            "port_code": location["port_code"],
            "country_id": location["country_id"],
            "continent_id": location["continent_id"],
            "trade_id": location["trade_id"],
            "country_code": location["country_code"],
        }
        return loc_data
