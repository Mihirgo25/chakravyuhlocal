from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from fastapi import HTTPException
from configs.definitions import AIR_FREIGHT_SURCHARGES


class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirFreightRateSurcharge(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    origin_airport_id=UUIDField(index=True,null=True)
    origin_country_id=UUIDField(null=True)
    origin_trade_id=UUIDField(null=True)
    origin_continent_id=UUIDField(null=True)
    destination_airport_id=UUIDField(index=True,null=True)
    destination_country_id=UUIDField(null=True)
    destination_trade_id=UUIDField(null=True)
    destination_continent_id=UUIDField(null=True)
    commodity=CharField(null=True,index=True)
    commodity_type=CharField(null=True)
    origin_airport=BinaryJSONField(null=True)
    destination_airport=BinaryJSONField(null=True)
    airline_id=UUIDField(null=True)
    service_provider_id=UUIDField(null=True)
    is_line_items_error_messages_present = BooleanField(null=True)
    is_line_items_info_messages_present = BooleanField(null=True)
    line_items = BinaryJSONField(null=True)
    line_items_error_messages = BinaryJSONField(null=True)
    line_items_info_messages = BinaryJSONField(null=True)
    airline=BinaryJSONField(null=True)
    service_provider=BinaryJSONField(null=True)
    origin_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    destination_location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, index=True, null=True)
    operation_type=CharField(null=True)
    sourced_by_id=UUIDField(null=True,index=True)
    procured_by_id=UUIDField(null=True,index=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by = BinaryJSONField(null=True)
    perform_by = BinaryJSONField(null=True)
    updated_at=DateTimeField(default=datetime.datetime.now,index=True)
    created_at=DateTimeField(default=datetime.datetime.now,index=True)

    class Meta:
        table_name = 'air_freight_rate_surcharges'

    def possible_charge_codes():
        charges = AIR_FREIGHT_SURCHARGES
        filtered_charges = [charge for charge in charges if eval(charge[-1]['condition'].to_s)]
        filtered_charges = [charge for charge in filtered_charges if charge]
        charges_dict = dict(filtered_charges)
        return charges_dict

    def detail(self):
        return {
        'freight': {
            'id': self.id,
            'validities': self.validities,
            'is_rate_expired': self.is_rate_expired(),
            'is_rate_about_to_expire': self.is_rate_about_to_expire(),
            'is_rate_not_available': self.is_rate_not_available()
        },
        'origin_local': {
            'id': self.origin_local.id,
            'line_items': self.origin_local.line_items,
            'line_items_info_messages': self.origin_local.line_items_info_messages,
            'is_line_items_info_messages_present': self.origin_local.is_line_items_info_messages_present,
            'line_items_error_messages': self.origin_local.line_items_error_messages,
            'is_line_items_error_messages_present': self.origin_local.is_line_items_error_messages_present
        },
        'destination_local': {
            'id': self.destination_local.id,
            'line_items': self.destination_local.line_items,
            'line_items_info_messages': self.destination_local.line_items_info_messages,
            'is_line_items_info_messages_present': self.destination_local.is_line_items_info_messages_present,
            'line_items_error_messages': self.destination_local.line_items_error_messages,
            'is_line_items_error_messages_present': self.destination_local.is_line_items_error_messages_present
        },
        'surcharge': {
            'id': self.surcharge.id,
            'line_items': self.surcharge.line_items,
            'line_items_info_messages': self.surcharge.line_items_info_messages,
            'is_line_items_info_messages_present': self.surcharge.is_line_items_info_messages_present,
            'line_items_error_messages': self.surcharge.line_items_error_messages,
            'is_line_items_error_messages_present': self.surcharge.is_line_items_error_messages_present
        }
    }


        
    


    


