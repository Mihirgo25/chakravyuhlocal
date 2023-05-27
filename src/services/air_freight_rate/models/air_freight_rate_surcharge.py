from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from services.air_freight_rate.models.air_freight_rate import AirFreightRate

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

    def update_line_item_messages(self):
        line_items_error_messages = {}
        line_items_info_messages = {}
        is_line_items_error_messages_present = False
        is_line_items_info_messages_present = False

        grouped_charge_codes = {}
        for line_item in self.line_items:
            if line_item['code'] not in grouped_charge_codes:
                grouped_charge_codes[line_item['code']] = []
            grouped_charge_codes[line_item['code']].append(line_item)

        for code, line_items in grouped_charge_codes.items():
            code_config = AIR_FREIGHT_SURCHARGES.get(code)

            if not code_config:
                line_items_error_messages[code] = ['is invalid']
                is_line_items_error_messages_present = True
                continue

            if len(set([item.unit for item in line_items]) - set(code_config['units'])) > 0:
                line_items_error_messages[code] = ["can only be having units " + ", ".join(code_config['units'])]
                is_line_items_error_messages_present = True
                continue

            if not eval(str(code_config['condition'])):
                line_items_error_messages[code] = ['is invalid']
                is_line_items_error_messages_present = True
                continue
        possible_charge_codes=possible_charge_codes()
        for code, config in possible_charge_codes.items():
            if 'mandatory' in config['tags']:
                if str(code) not in grouped_charge_codes:
                    line_items_error_messages[code] = ['is not present']
                    is_line_items_error_messages_present = True

        for code, config in possible_charge_codes.items():
            if 'additional_service' in config['tags'] or 'shipment_execution_service' in config['tags']:
                if str(code) not in grouped_charge_codes:
                    line_items_info_messages[code] = ['can be added for more conversion']
                    is_line_items_info_messages_present = True

        self.line_items_error_messages = line_items_error_messages
        self.line_items_info_messages = line_items_info_messages
        self.is_line_items_info_messages_present = is_line_items_info_messages_present
        self.is_line_items_error_messages_present = is_line_items_error_messages_present
        self.save()
    
    def update_freight_objects(self):
        freight_query = AirFreightRate.select(AirFreightRate.id).where(
            (AirFreightRate.origin_airport_id == self.origin_airport_id),
            (AirFreightRate.destination_airport_id == self.destination_airport_id),
            (AirFreightRate.commodity == self.commodity) ,
            (AirFreightRate.commodity_type == self.commodity_type) ,
            (AirFreightRate.operation_type == self.operation_type) ,
            (AirFreightRate.airline_id == self.airline_id) ,
            (AirFreightRate.service_provider == self.service_provider_id),
            (getattr(AirFreightRate, "surcharge_id" == None)),
            (getattr(AirFreightRate, "price_type" == "net_net"))).update(surcharge_id=self.id)
      







        
    


    


