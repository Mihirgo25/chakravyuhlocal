import re, datetime
from peewee import *
from fastapi import HTTPException
from database.db_session import db
from playhouse.postgres_ext import *
from configs.ftl_freight_rate_constants import (
    RATE_TYPES,
    BODY_TYPE,
    TRIP_TYPES,
    VALID_UNITS,
    COMMODITIES,
    DEFAULT_FTL_NOTIFICATION_RECIPIENT_ID,
)
from micro_services.client import maps, common
from configs.definitions import FTL_FREIGHT_CHARGES
from libs.get_applicable_filters import is_valid_uuid
from fastapi.encoders import jsonable_encoder
from database.rails_db import get_eligible_orgs


class UnknownField(object):
    def __init__(self, *_, **__):
        pass


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True


class FtlFreightRate(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_location_id = UUIDField(null=True, index=True)
    origin_cluster_id = UUIDField(null=True, index=True)
    origin_country_id = UUIDField(null=True, index=True)
    origin_city_id = UUIDField(null=True, index=True)
    origin_location_type = CharField(null=True, index=True)
    origin_location_ids = ArrayField(
        constraints=[SQL("DEFAULT '{}'::uuid[]")],
        field_class=UUIDField,
        index=True,
        null=True,
    )
    destination_location_id = UUIDField(null=True, index=True)
    destination_cluster_id = UUIDField(null=True, index=True)
    destination_country_id = UUIDField(null=True, index=True)
    destination_city_id = UUIDField(null=True, index=True)
    destination_location_type = CharField(null=True, index=True)
    destination_location_ids = ArrayField(
        constraints=[SQL("DEFAULT '{}'::uuid[]")],
        field_class=UUIDField,
        index=True,
        null=True,
    )
    origin_destination_location_type = CharField(null=True, index=True)
    commodity = TextField(null=True, index=True)
    service_provider_id = UUIDField(index=True, null=True)
    importer_exporter_id = UUIDField(null=True)
    importer_exporters_count = IntegerField(null=True)
    line_items = BinaryJSONField(default=[], null=True)
    platform_price = FloatField(null=True)
    is_best_price = BooleanField(null=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items_error_messages = BinaryJSONField(null=True)
    line_items_info_messages = BinaryJSONField(null=True)
    truck_type = TextField(null=True, index=True)
    truck_body_type = TextField(index=True, null=True)
    trip_type = CharField(index=True, null=True)
    minimum_chargeable_weight = FloatField(index=True, null=True)
    transit_time = IntegerField(index=True, null=True)
    unit = CharField(index=True, null=True)
    trucks_count = IntegerField(null=True)
    rate_not_available_entry = BooleanField(
        constraints=[SQL("DEFAULT false")], null=True, index=True
    )
    validity_start = DateField(index=True, null=True)
    validity_end = DateField(
        index=True, default=datetime.date.today() + datetime.timedelta(15), null=True
    )
    detention_free_time = IntegerField(index=True, null=True)
    importer_exporter = BinaryJSONField(null=True)
    service_provider = BinaryJSONField(null=True)
    origin_location = BinaryJSONField(index=True, null=True)
    destination_location = BinaryJSONField(index=True, null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now, index=True)
    source = CharField(default="manual", index=True, null=True)
    accuracy = FloatField(default=100, null=True)
    sourced_by_id = UUIDField(null=True, index=True)
    procured_by_id = UUIDField(null=True, index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    rate_type = CharField(default="market_place", choices=RATE_TYPES, index=True)
    tags = BinaryJSONField(null=True)
    init_key = TextField(index=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FtlFreightRate, self).save(*args, **kwargs)

    class Meta:
        table_name = "ftl_freight_rates"

    def set_locations(self):
        ids = [str(self.origin_location_id), str(self.destination_location_id)]
        locations_response = maps.list_locations(
            {
                "filters": {"id": ids},
                "includes": {
                    "id": True,
                    "name": True,
                    "type": True,
                    "is_icd": True,
                    "cluster_id": True,
                    "city_id": True,
                    "country_id": True,
                    "country_code": True,
                    "display_name": True,
                    "postal_code": True,
                },
            }
        )
        locations = []
        if "list" in locations_response:
            locations = locations_response["list"]
        for location in locations:
            if str(location["id"]) == str(self.origin_location_id):
                self.origin_location = self.get_required_location_data(location)
            if str(location["id"]) == str(self.destination_location_id):
                self.destination_location = self.get_required_location_data(location)
        self.set_origin_location_ids()
        self.set_origin_location_type()
        self.set_destination_location_ids()
        self.set_destination_location_type()
        self.set_origin_destination_location_type()

    def get_required_location_data(self, location):
        loc_data = {
            "id": location["id"],
            "name": location["name"],
            "is_icd": location["is_icd"],
            "type": location["type"],
            "cluster_id": location["cluster_id"],
            "city_id": location["city_id"],
            "country_id": location["country_id"],
            "country_code": location["country_code"],
            "display_name": location["display_name"],
            "postal_code": location["postal_code"],
        }
        return loc_data

    def set_origin_location_ids(self):
        self.origin_cluster_id = self.origin_location.get("cluster_id")
        self.origin_city_id = self.origin_location.get("city_id")
        self.origin_country_id = self.origin_location.get("country_id")
        ids = [
            self.origin_location_id,
            self.origin_cluster_id,
            self.origin_city_id,
            self.origin_country_id,
        ]
        self.origin_location_ids = []
        for id in ids:
            if is_valid_uuid(id):
                if type(id) == str:
                    self.origin_location_ids.append(uuid.UUID(id))
                else:
                    self.origin_location_ids.append(id)

    def set_origin_location_type(self):
        self.origin_location_type = self.origin_location.get("type")

    def set_destination_location_ids(self):
        self.destination_cluster_id = self.destination_location.get("cluster_id")
        self.destination_city_id = self.destination_location.get("city_id")
        self.destination_country_id = self.destination_location.get("country_id")
        ids = [
            self.destination_location_id,
            self.destination_cluster_id,
            self.destination_city_id,
            self.destination_country_id,
        ]
        self.destination_location_ids = []
        for id in ids:
            if is_valid_uuid(id):
                if type(id) == str:
                    self.destination_location_ids.append(uuid.UUID(id))
                else:
                    self.destination_location_ids.append(id)

    def set_destination_location_type(self):
        self.destination_location_type = self.destination_location.get("type")

    def set_origin_destination_location_type(self):
        self.origin_destination_location_type = ":".join(
            [str(self.origin_location_type), str(self.destination_location_type)]
        )

    def validate_validities(self, validity_start, validity_end):
        if not validity_start:
            raise HTTPException(status_code=400, detail="validity_start is invalid")

        if not validity_end:
            raise HTTPException(status_code=400, detail="validity_end is invalid")

        if validity_end < validity_start:
            raise HTTPException(
                status_code=400,
                detail="validity_end can not be lesser than validity_start",
            )

    def validate_duplicate_line_items(self):
        self.line_items = self.line_items or []
        if len(set(map(lambda t: str(t["code"]).upper(), self.line_items))) != len(
            self.line_items
        ):
            raise HTTPException(status_code=403, detail="Contains Duplicates")

    def validate_truck_body_type(self):
        if self.truck_body_type not in BODY_TYPE:
            raise HTTPException(status_code=400, detail="Invalid truck_body_type")

    def validate_trip_type(self):
        if self.trip_type not in TRIP_TYPES:
            raise HTTPException(status_code=400, detail="Invalid trip_type")

    def validate_origin_destination_locations(self):
        if (
            self.origin_location_id == self.destination_location_id
            and self.origin_location_type == "pincode"
        ):
            raise HTTPException(
                status_code=400,
                detail="origin_location and destination_location can not be same",
            )

    def validate_minimum_chargeable_weight(self):
        if self.unit == "per_ton" and not self.minimum_chargeable_weight:
            raise HTTPException(
                status_code=400, detail="minimum_chargeable_weight is required"
            )

    def validate_unit(self):
        if self.unit and self.unit not in VALID_UNITS:
            raise HTTPException(status_code=400, detail="Invalid unit")

    def validate_transit_time(self):
        if self.transit_time <= 0:
            raise HTTPException(status_code=400, detail="Invalid transit_time")

    def validate_detention_free_time(self):
        if self.detention_free_time < 0:
            raise HTTPException(status_code=400, detail="Invalid detention_free_time")

    def validate_commodity(self):
        if self.commodity not in COMMODITIES:
            raise HTTPException(status_code=400, detail="Invalid commodity")

    def validate_service_provider_id(self):
        eligible_service_providers = get_eligible_orgs(service="ftl_freight")
        if str(self.service_provider_id) not in eligible_service_providers:
            raise HTTPException(status_code=400, detail="Invalid service provider ID")

    def validate_before_save(self):
        self.validate_duplicate_line_items()
        self.validate_truck_body_type()
        self.validate_trip_type()
        self.validate_origin_destination_locations()
        self.validate_unit()
        self.validate_minimum_chargeable_weight()
        self.validate_transit_time()
        self.validate_detention_free_time()
        self.validate_commodity()
        self.validate_service_provider_id()

    def mandatory_charge_codes(self, possible_charge_codes):
        charge_codes = {}
        for code, config in possible_charge_codes.items():
            if "mandatory" in config["tags"]:
                charge_codes[code.upper()] = config

        return charge_codes

    def get_money_exchange_for_fcl(self, param, currency):
        exchange_price = 0
        if param["currency"] != currency:
            exchange_price = int(
                common.get_money_exchange_for_fcl(
                    {
                        "price": param["price"],
                        "from_currency": param["currency"],
                        "to_currency": currency,
                    }
                )["price"]
            )
        return exchange_price

    def get_line_items_total_price(self, line_items):
        currency = line_items[0].get("currency")
        result = 0
        for line_item in line_items:
            result = result + self.get_money_exchange_for_fcl(line_item, currency)
        return result

    def get_mandatory_line_items(self, mandatory_charge_codes):
        mandatory_line_items = [
            line_item
            for line_item in self.line_items
            if str((line_item.get("code") or "").upper()) in mandatory_charge_codes
        ]
        return mandatory_line_items

    def set_platform_price(self):
        possible_charge_codes = self.possible_charge_codes()
        mandatory_charge_codes = self.mandatory_charge_codes(possible_charge_codes)
        line_items = self.get_mandatory_line_items(mandatory_charge_codes)
        if not line_items:
            return
        currency = self.line_items[0].get("currency")

        result = self.get_line_items_total_price(line_items)

        rates = (
            FtlFreightRate.select(FtlFreightRate.line_items)
            .where(
                FtlFreightRate.origin_location_id == self.origin_location_id,
                FtlFreightRate.destination_location_id == self.destination_location_id,
                FtlFreightRate.truck_type == self.truck_type,
                FtlFreightRate.truck_body_type == self.truck_body_type,
                FtlFreightRate.commodity == self.commodity,
                FtlFreightRate.is_line_items_error_messages_present == False,
            )
            .where(
                FtlFreightRate.importer_exporter_id.is_null(True)
                | (FtlFreightRate.importer_exporter_id == self.importer_exporter_id)
            )
        )

        ftl_freight_rates = jsonable_encoder(list(rates.dicts()))
        sum = 0
        if len(rates) > 0:
            for rate in ftl_freight_rates:
                mandatory_line_items = [
                    line_item
                    for line_item in rate.get("line_items")
                    if str((line_item.get("code") or "").upper())
                    in mandatory_charge_codes
                ]
                for prices in mandatory_line_items:
                    sum = sum + self.get_money_exchange_for_fcl(prices, currency)
                if sum and result > sum:
                    result = sum

        self.platform_price = result

    def set_is_best_price(self):
        if not self.platform_price:
            return

        possible_charge_codes = self.possible_charge_codes()
        mandatory_charge_codes = self.mandatory_charge_codes(possible_charge_codes)
        line_items = self.get_mandatory_line_items(mandatory_charge_codes)

        total_price = self.get_line_items_total_price(line_items)

        self.is_best_price = total_price <= self.platform_price

    def update_platform_prices_for_other_service_providers(self):
        from services.ftl_freight_rate.interactions.update_ftl_freight_rate_platform_prices import (
            update_ftl_freight_rate_platform_prices,
        )

        data = {
            "origin_location_id": self.origin_location_id,
            "destination_location_id": self.destination_location_id,
            "container_size": self.truck_type,
            "container_type": self.truck_body_type,
            "commodity": self.commodity,
            "importer_exporter_id": self.importer_exporter_id,
        }

        update_ftl_freight_rate_platform_prices(data)

    def update_line_item_messages(self, possible_charge_codes):
        self.line_items_error_messages = {}
        self.line_items_info_messages = {}
        self.is_line_items_error_messages_present = False
        self.is_line_items_info_messages_present = False

        grouped_charge_codes = {}

        for line_item in self.line_items:
            if grouped_charge_codes.get(line_item.get("code")):
                item = grouped_charge_codes[line_item.get("code")]
            else:
                item = []
            grouped_charge_codes[line_item.get("code")] = item + [line_item]

        for code, line_items in grouped_charge_codes.items():
            code_config = FTL_FREIGHT_CHARGES.get()[code]

            if not code_config:
                self.line_items_error_messages[code] = ["is invalid"]
                self.is_line_items_error_messages_present = True
                continue

            if (
                len(
                    set(map(lambda item: item.get("unit"), line_items))
                    - set(code_config["units"])
                )
                > 0
            ):
                self.line_items_error_messages[code] = [
                    "can only be having units " + ", ".join(code_config["units"])
                ]
                self.is_line_items_error_messages_present = True
                continue

            if not eval(str(code_config.get("condition"))):
                self.line_items_error_messages[code] = ["is invalid"]
                self.is_line_items_error_messages_present = True
                continue

        for code, config in possible_charge_codes.items():
            if "mandatory" in config.get("tags", []):
                if code not in grouped_charge_codes:
                    self.line_items_error_messages[code] = ["is not present"]
                    self.is_line_items_error_messages_present = True

        for code, config in possible_charge_codes.items():
            if "additional_service" in config.get(
                "tags", []
            ) or "shipment_execution_service" in config.get("tags", []):
                if code not in grouped_charge_codes:
                    self.line_items_info_messages[code] = [
                        "can be added for more conversion"
                    ]
                    self.is_line_items_info_messages_present = True

        return {
            "line_items_error_messages": self.line_items_error_messages,
            "is_line_items_error_messages_present": self.is_line_items_error_messages_present,
            "line_items_info_messages": self.line_items_info_messages,
            "is_line_items_info_messages_present": self.is_line_items_info_messages_present,
        }

    def detail(self):
        ftl_freight = {
            "transit_time": self.transit_time,
            "detention_free_time": self.detention_free_time,
            "truck_body_type": self.truck_body_type,
            "validity_start": self.validity_start,
            "validity_end": self.validity_end,
            "line_items": self.line_items,
            "line_items_info_messages": self.line_items_info_messages,
            "is_line_items_info_messages_present": self.is_line_items_info_messages_present,
            "line_items_error_messages": self.line_items_error_messages,
            "is_line_items_error_messages_present": self.is_line_items_error_messages_present,
            "unit": self.unit,
            "minimum_chargeable_weight": self.minimum_chargeable_weight,
        }

        return {"ftl_freight": ftl_freight}

    def possible_charge_codes(self):
        ftl_freight_charges_dict = FTL_FREIGHT_CHARGES.get()

        charge_codes = {}

        for code, config in ftl_freight_charges_dict.items():
            if eval(str(config["condition"])):
                charge_codes[code] = config
        return charge_codes

    def send_missing_or_dislike_rate_notifications_to_kam(
        self, query_raised_by_id, is_rate_missing_or_dislike
    ):
        origin_location = self.origin_location
        destination_location = self.destination_location

        shubham_id = DEFAULT_FTL_NOTIFICATION_RECIPIENT_ID

        for user in (
            [query_raised_by_id, shubham_id]
            if query_raised_by_id is not None
            else [shubham_id]
        ):
            notification_data = {
                "type": "platform_notification",
                "user_id": user,
                "service": "ftl_freight_rate",
                "service_id": self.id,
                "template_name": "missing_or_dislike_rate_revert",
                "service_objects": [
                    {"service": "user", "id": user, "alias": "service_ops1"}
                ],
                "variables": {
                    "service_type": "ftl_freight_service",
                    "origin": origin_location.get("name"),
                    "destination": destination_location.get("name"),
                    "truck_type": self.truck_type,
                    "commodity": self.commodity,
                    "missing_or_dislike": is_rate_missing_or_dislike,
                    "validity_start": self.validity_start.date(),
                    "validity_end": self.validity_end.date(),
                },
            }
            common.create_communication(notification_data)

    def send_missing_or_dislike_rate_notifications_to_platform(
        self, query_raised_by_id, is_rate_missing_or_dislike
    ):
        origin_location = self.origin_location
        destination_location = self.destination_location

        shubham_id = DEFAULT_FTL_NOTIFICATION_RECIPIENT_ID

        for user in (
            [query_raised_by_id, shubham_id]
            if query_raised_by_id is not None
            else [shubham_id]
        ):
            notification_data = {
                "type": "platform_notification",
                "user_id": user,
                "service": "ftl_freight_rate",
                "service_id": self.id,
                "template_name": "missing_or_dislike_rate_platform_notification_revert",
                "variables": {
                    "service_type": "ftl_freight_service",
                    "origin": origin_location.get("name"),
                    "destination": destination_location.get("name"),
                    "truck_type": self.truck_type,
                    "commodity": self.commodity
                    if self.commodity is not None
                    else "general",
                    "missing_or_dislike": is_rate_missing_or_dislike,
                    "validity_start": self.validity_start.date(),
                    "validity_end": self.validity_end.date(),
                },
            }
            common.create_communication(notification_data)
