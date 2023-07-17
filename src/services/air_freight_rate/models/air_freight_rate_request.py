from peewee import *
from database.db_session import db
from services.air_freight_rate.constants.air_freight_rate_constants import REQUEST_SOURCES
from fastapi import HTTPException
from micro_services.client import *
from database.rails_db import *
from playhouse.postgres_ext import *
import datetime
from fastapi.encoders import jsonable_encoder


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class AirFreightRateRequest(BaseModel):
    booking_params = BinaryJSONField(null=True)
    cargo_readiness_date = DateTimeField(null=True)
    cogo_entity_id = UUIDField(null=True,index=True)
    cargo_stacking_type = CharField(null=True)
    closed_by_id = UUIDField(null=True,index=True)
    closing_remarks = ArrayField(field_class=TextField, null=True)
    commodity = CharField(null=True,index=True)
    commodity_sub_type = TextField(null=True,index=True)
    commodity_type = TextField(null=True,index=True)
    created_at = DateTimeField(index=True, default=datetime.datetime.now)
    destination_airport_id = UUIDField(null=True,index=True)
    destination_airport = BinaryJSONField(null=True)
    destination_continent_id = UUIDField(null=True,index=True)
    destination_country_id = UUIDField(null=True,index=True)
    destination_trade_id = UUIDField(null=True,index=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    reverted_by_user_ids = ArrayField(field_class=UUIDField, null=True)
    reverted_rates_count = IntegerField(null=True,default=0)
    inco_term = CharField(null=True)
    origin_airport_id = UUIDField(null=True,index=True)
    origin_airport = BinaryJSONField(null=True)
    origin_continent_id = UUIDField(null=True,index=True)
    origin_country_id = UUIDField(null=True,index=True)
    origin_trade_id = UUIDField(null=True,index=True)
    packages = BinaryJSONField(null=True)
    packages_count = IntegerField(null=True)
    performed_by_id = UUIDField(null=True,index=True)
    performed_by = BinaryJSONField(null=True)
    performed_by_org_id = CharField(null=True,index=True)
    performed_by_type = CharField(null=True)
    airline_id = UUIDField(null=True,index=True)
    service_provider_id = UUIDField(null=True,index=True)
    service_provider = BinaryJSONField(null=True)
    price_type = CharField(null=True)
    operation_type = CharField(null=True)
    preferred_airlines = BinaryJSONField(null=True)
    preferred_airline_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    preferred_detention_free_days = IntegerField(null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    preferred_storage_free_days = IntegerField(null=True)
    remarks = ArrayField(field_class=TextField, null=True)
    request_type = CharField(null=True)
    serial_id = BigIntegerField(
        constraints=[
            SQL("DEFAULT nextval('air_freight_rate_requests_serial_id_seq'::regclass)")
        ]
    )
    source = CharField(null=True)
    source_id = UUIDField(null=True,index=True)
    status = CharField(null=True,index=True, default="active")
    trade_type = CharField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    volume = DoubleField(null=True)
    weight = DoubleField(null=True)

    class Meta:
        table_name = "air_freight_rate_requests"

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(AirFreightRateRequest, self).save(*args, **kwargs)

    def validate(self):
        # self.validate_source()
        # self.validate_source_id()
        # self.validate_performed_by_id()
        # self.validate_performed_by_org_id()
        self.validate_preferred_airline_ids()
        return True

    def validate_source(self):
        if self.source and self.source not in REQUEST_SOURCES:
            raise HTTPException(status_code=400, detail="Invalid source")

    def validate_source_id(self):
        if self.source == "spot_search":
            spot_search_data = spot_search.list_spot_searches(
                {"filters": {"id": [str(self.source_id)]}}
            )["list"]
            if len(spot_search_data) == 0:
                raise HTTPException(status_code=400, detail="Invalid Source ID")

    def validate_performed_by_id(self):
        if self.performed_by_id:
            data = get_user(str(self.performed_by_id))

            if data:
                pass
            else:
                raise HTTPException(status_code=400, detail="Invalid Performed by ID")
        return True

    def validate_performed_by_org_id(self):
        performed_by_org_data = get_organization(id=str(self.performed_by_org_id))
        if (
            len(performed_by_org_data) == 0
            or performed_by_org_data[0]["account_type"] != "importer_exporter"
        ):
            raise HTTPException(status_code=400, detail="Invalid Account Type")

    def validate_preferred_airline_ids(self):
        if not self.preferred_airline_ids:
            pass
        if self.preferred_airline_ids:
            # need to change the name to get operators name
            airline_data = get_operators(id=self.preferred_airline_ids)
            if len(airline_data) != len(self.preferred_airline_ids):
                raise HTTPException(status_code=400, detail="Invalid Shipping Line ID")
            self.preferred_airlines = airline_data
            self.preferred_airline_ids = [
                uuid.UUID(str(ariline_id)) for ariline_id in self.preferred_airline_ids
            ]

    def send_closed_notifications_to_sales_agent(self):
        location_pair = (
            AirFreightRateRequest.select(
                AirFreightRateRequest.origin_airport_id,
                AirFreightRateRequest.destination_airport_id,
            )
            .where(AirFreightRateRequest.source_id == self.source_id).first())
        location_pair_data = maps.list_locations(
            {
                "filters": {
                    "id": [
                        str(location_pair.origin_airport_id),
                        str(location_pair.destination_airport_id),
                    ]
                }
            }
        )["list"]
        location_pair_name = {
            data["id"]: data["display_name"] for data in location_pair_data
        }

        try:
            importer_exporter_id = spot_search.get_spot_search(
                {"id": str(self.source_id)}
            )["detail"]["importer_exporter_id"]
        except:
            importer_exporter_id = None
        origin_location = location_pair_name[str(location_pair.origin_airport_id)]
        destination_location = location_pair_name[
            str(location_pair.destination_airport_id)
        ]

        data = {
            "user_id": self.performed_by_id,
            "type": "platform_notification",
            "service": "air_freight_rate",
            "service_id": self.id,
            "template_name": "freight_rate_request_completed_notification"
            if "rate_added" in self.closing_remarks
            else "freight_rate_request_closed_notification",
            "variables": {
                "service_type": "air freight",
                "origin_location": origin_location,
                "destination_location": destination_location,
                "remarks": None
                if "rate_added" in self.closing_remarks
                else "Reason: {}.".format(
                    self.closing_remarks[0].lower().replace("_", " ")
                ),
                "request_serial_id": str(self.serial_id),
                "spot_search_id": str(self.source_id),
                "importer_exporter_id": importer_exporter_id,
            },
        }
        push_notification_data = self.get_push_notification_data(location_pair_name,location_pair)
        common.create_communication(push_notification_data)
        common.create_communication(data)

    def get_push_notification_data(self,location_pair_name,location_pair):
        if  'rate_added'  in self.closing_remarks:
            subject = 'Freight Rate Request Completed'
            body = f"Rate has been added for Request No: {self.serial_id}, air freight from {location_pair_name[str(location_pair.origin_airport_id)]} to {location_pair_name[str(location_pair.destination_airport_id)]}."
        else:
            subject ='Freight Rate Request Closed'
            remarks = f"Reason: #{self.closing_remarks[0]}."
            body = f"Your rate request has been closed for Request No: {self.serial_id}, air freight from {location_pair_name[str(location_pair.origin_airport_id)]} to {location_pair_name[(location_pair.destination_airport_id)]}. #{remarks}"

        return {
            'type':'push_notification',
            'service':'air_freight_rate',
            'service_id':str(self.id),
            'provider_name':'firebase',
            'template_name':'push_notification',
            'user_id':str(self.performed_by_id),
            'variables':{
                'subject':subject,
                'body':body,
                'notification_source':'spot_search',
                'notification_source_id':str(self.source_id)
            }
        }

    def set_locations(self):
        ids = [str(self.origin_airport_id), str(self.destination_airport_id)]
        obj = {"filters": {"id": ids, "type": "airport"}}
        locations_response = maps.list_locations(obj)["list"]

        for location in locations_response:
            if str(self.origin_airport_id) == str(location["id"]):
                self.origin_airport = self.get_required_location_data(location)
            if str(self.destination_airport_id) == str(location["id"]):
                self.destination_airport = self.get_required_location_data(location)

    def get_required_location_data(self, location):
        loc_data = {
            "id": location["id"],
            "name": location["name"],
            "port_code": location["port_code"],
            "name": location["name"],
            "display_name": location["display_name"],
        }
        return loc_data
