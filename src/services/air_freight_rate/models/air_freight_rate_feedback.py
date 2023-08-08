from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
from services.air_freight_rate.constants.air_freight_rate_constants import *
from micro_services.client import *
from database.rails_db import *
from services.air_freight_rate.models.air_freight_rate import AirFreightRate
import datetime
from fastapi.encoders import jsonable_encoder


class UnknownField(object):
    def __init__(self, *_, **__):
        pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateFeedback(BaseModel):
    air_freight_rate_id = UUIDField(null=True,index=True)
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
    preferred_airline_ids = ArrayField(field_class=UUIDField, null=True)
    preferred_airlines = BinaryJSONField(null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    preferred_storage_free_days = IntegerField(null=True)
    remarks = ArrayField(field_class=TextField, null=True)
    serial_id = BigIntegerField(
        constraints=[
            SQL("DEFAULT nextval('air_freight_rate_feedback_serial_id_seq'::regclass)")
        ]
    )
    source = CharField(null=True)
    source_id = UUIDField(null=True,index=True)
    status = CharField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    validity_id = UUIDField(null=True)
    closed_by = BinaryJSONField(null=True)
    reverted_rate_id = UUIDField(null=True, index=True)
    reverted_rate= BinaryJSONField(null=True)
    origin_airport_id = UUIDField(null=True, index=True)
    origin_country_id = UUIDField(null=True, index=True)
    origin_continent_id = UUIDField(null=True, index=True)
    origin_trade_id = UUIDField(null=True, index=True)
    destination_airport_id = UUIDField(null=True, index=True)
    destination_country_id = UUIDField(null=True, index=True)
    destination_continent_id = UUIDField(null=True, index=True)
    destination_trade_id = UUIDField(null=True, index=True)
    cogo_entity_id = UUIDField(null=True, index=True)
    service_provider_id = UUIDField(null=True, index=True)
    commodity = TextField(null=True,index=True)
    operation_type = TextField(null=True,index=True)
    airline_id=UUIDField(null=True,index=True)

    class Meta:
        table_name = "air_freight_rate_feedbacks"
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(AirFreightRateFeedback, self).save(*args, **kwargs)

    def supply_agents_notify(self):
        locations_data = (
            AirFreightRate.select(
                AirFreightRate.origin_airport_id,
                AirFreightRate.origin_country_id,
                AirFreightRate.origin_continent_id,
                AirFreightRate.origin_trade_id,
                AirFreightRate.destination_airport_id,
                AirFreightRate.destination_country_id,
                AirFreightRate.destination_continent_id,
                AirFreightRate.destination_trade_id,
                AirFreightRate.commodity
            )
            .where(AirFreightRate.id == self.air_freight_rate_id)
            .first()
        )

        if locations_data:
            origin_locations = [
                locations_data.origin_airport_id,
                locations_data.origin_counrtry_id,
                locations_data.origin_continent_id,
                locations_data.origin_trade_id,
            ]
            origin_locations = [str(t) for t in origin_locations if t is not None]
        else:
            origin_locations = []

        if locations_data:
            destination_locations = [
                locations_data.destination_airport,
                locations_data.destination_counrtry_id,
                locations_data.destination_continent_id,
                locations_data.destination_trade_id,
            ]
            destination_locations = [str(t) for t in destination_locations if t is not None]
        else:
            destination_locations = []

        supply_agents_list = get_partner_users_by_expertise(
            service="air_freight", origin_location_ids = origin_locations, destination_location_ids = destination_locations
        )

        supply_agents_list = list(set(t["partner_user_id"] for t in supply_agents_list))

        supply_agents_user_ids = get_partner_users(supply_agents_list)

        supply_agents_user_ids = list(set(t["user_id"] for t in supply_agents_user_ids))

        route = maps.list_locations(
            {
                "filters": {
                    "id": [
                        str(locations_data.origin_airport_id),
                        str(locations_data.destination_airport_id),
                    ]
                }
            }
        )["list"]

        route = {t["id"]: t["display_name"] for t in route}

        return {
            "user_ids": supply_agents_user_ids,
            "origin_location": route[str(locations_data.origin_airport_id)],
            "destination_location": route[str(locations_data.destination_airport_id)],
            "commodity": locations_data.commodity,
        }

    def send_create_notifications_to_supply_agents(self):
        feedback_info = self.supply_agents_notify()
        commodity = ""
        if "commodity_type" in feedback_info and feedback_info["commodity_type"]:
            commodity = feedback_info["commodity_type"].upper()
        origin_airport = feedback_info["origin_location"]
        destination_airport = feedback_info["destination_location"]
        data = {
            "type": "platform_notification",
            "service": "air_freight_rate",
            "service_id": str(self.id),
            "template_name": "freight_rate_disliked",
            "variables": {
                "service_type": "air freight",
                "origin_port": origin_airport,
                "destination_port": destination_airport,
                "details": {"commodity": commodity},
            },
        }
        for user_id in feedback_info["user_ids"]:
            data["user_id"] = user_id
            common.create_communication(data)

    def send_closed_notifications_to_sales_agent(self):
        variables_data = {}
        reverted_rates = AirFreightRate.select(AirFreightRate.airline_id,AirFreightRate.price_type).where(AirFreightRate.id == self.reverted_rate_id).first()
        locations_data = AirFreightRate.select( 
            AirFreightRate.origin_airport_id,
            AirFreightRate.destination_airport_id,
            AirFreightRate.airline_id,
            AirFreightRate.price_type
            ).where(AirFreightRate.id == self.air_freight_rate_id)
        locations_data = jsonable_encoder(list(locations_data.dicts()))
        variables_data['locations_data'] = locations_data[0]

        if reverted_rates:
            reverted_airline = get_operators(id=str(reverted_rates.airline_id))
            variables_data['changed_components'] = ''
            if reverted_airline:
                reverted_airline = reverted_airline[0]['short_name']
                variables_data['changed_components'] += f'with new airline {reverted_airline}' if str(reverted_rates.airline_id) != variables_data['locations_data']['airline_id'] else ""
            variables_data['changed_components'] += f'with new price type {reverted_rates.price_type}' if reverted_rates.price_type != variables_data['locations_data']['price_type'] else ""
            variables_data['changed_components'] += '.'
        locations = [variables_data['locations_data']['origin_airport_id'],variables_data['locations_data']['destination_airport_id']]
        variables_data['location_pair_name'] = maps.list_locations({'filters':{ 'id':locations }})['list']
        variables_data['importer_exporter_id'] = spot_search.get_spot_search({'id':str(self.source_id)})['detail']['importer_exporter_id']
        
        if variables_data['location_pair_name'][0]['id']==variables_data['locations_data']['origin_airport_id']:
            location_pair_name = variables_data['location_pair_name']
        else:
            destination  = variables_data['location_pair_name'][0]
            location_pair_name = [variables_data['location_pair_name'][1],destination]
        locations_data = variables_data['locations_data']
        importer_exporter_id = variables_data['importer_exporter_id']
        changed_components = variables_data.get('changed_components')

        data = {
            "user_id": str(self.performed_by_id),
            "type": "platform_notification",
            "service": "air_freight_rate",
            "service_id": str(self.id),
            "template_name": "freight_rate_feedback_completed_notification_for_air" if ("rate_added" in self.closing_remarks) else "freight_rate_feedback_closed_notification",
            "variables": {
                "service_type": "air freight",
                "origin_location": location_pair_name[0].get('display_name'),
                "destination_location": location_pair_name[1].get('display_name'),
                "remarks": None
                if ("rate_added" in self.closing_remarks)
                else f"Reason: {self.closing_remarks[0].lower().replace('_', ' ')}",
                "request_serial_id": str(self.serial_id),
                "spot_search_id": str(self.source_id),
                "importer_exporter_id": importer_exporter_id,
                "changed_components" :changed_components
            },
        }
        common.create_communication(data)

    def validate_trade_type(self):
        if self.trade_type not in ["import", "export", "domestic"]:
            raise HTTPException(status_code=400, detail="invalid trade_type")

    def validate_feedback_type(self):
        if self.feedback_type not in FEEDBACK_TYPES:
            raise HTTPException(status_code=400, detail="invalid feedback type")

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
        return True

    def validate_preferred_storage_free_days(self):
        if  self.preferred_storage_free_days and not self.preferred_storage_free_days >= 0:
            raise HTTPException(
                status_code=400, detail="freedays should be greater than zero"
            )

    def validate_feedbacks(self):
        if self.feedbacks:
            for feedback in self.feedbacks:
                if feedback not in POSSIBLE_FEEDBACKS:
                    raise HTTPException(status_code=400, detail="invalid feedback")

    def validate_perform_by_org_id(self):
        performed_by_org_data = get_organization(id=self.performed_by_org_id)
        if (
            len(performed_by_org_data) > 0
            and performed_by_org_data[0]["account_type"] == "importer_exporter"
        ):
            return True
        else:
            raise HTTPException(status_code=400, detail="invalid org id ")

    def validate_source(self):
        if self.source and self.source not in FEEDBACK_SOURCES:
            raise HTTPException(status_code=400, detail="invalid feedback source")

    def validate_source_id(self):
        if self.source == "spot_search":
            spot_search_data = spot_search.list_spot_searches(
                {"filters": {"id": [str(self.source_id)]}}
            )
            if "list" in spot_search_data and len(spot_search_data["list"]) != 0:
                return True
        if self.source == "checkout":
            checkout_data = checkout.list_checkouts(
                {"filters": {"id": [str(self.source_id)]}}
            )
            if "list" in checkout_data and len(checkout_data["list"]) != 0:
                return True
        raise HTTPException(status_code=400, detail="invalid source id")

    def validate_performed_by_id(self):
        if self.performed_by_id:
            performed_by = get_user(id=str(self.performed_by_id))
            if not performed_by:
                raise HTTPException(status_code=400, detail="Invalid Performed By Id")
        return True

    def validate_before_save(self):
        self.validate_trade_type()
        self.validate_feedback_type()
        self.validate_preferred_airline_ids()
        self.validate_preferred_storage_free_days()
        self.validate_feedbacks()
        # self.validate_perform_by_org_id()
        self.validate_source()
        # self.validate_source_id()
        # self.validate_performed_by_id()
        return True
    
    def send_notification_to_supply_agents(self,air_freight_rate,airports):
        if air_freight_rate.procured_by_id:
            commodity = air_freight_rate.commodity
            if len(airports) < 2:
                return
            origin_airport = airports[0]
            destination_airport = airports[1]
            notification_data = {
                'type': 'platform_notification',
                'user_id': str(air_freight_rate.procured_by_id),
                'service': 'air_freight_rate',
                'service_id': str(air_freight_rate.id),
                'template_name': 'freight_rate_disliked',
                'variables': {
                    "origin_port": origin_airport.get('display_name'),
                    "destination_port": destination_airport.get('display_name'),
                    'service_type': 'air freight',
                    'details': "commodity : {}".format(commodity.upper())
                }
            }
            common.create_communication(notification_data)


    def send_closed_notifications_to_user_feedback(self):
           
           params = {
               'spot_search_id':str(self.source_id),
               'update_to_id':str(self.performed_by_id),
               'update_to_type':str(self.performed_by_type)
            } 
           spot_search.send_spot_search_rate_update(params)

           

