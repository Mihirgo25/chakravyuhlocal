from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from configs.fcl_freight_rate_constants import FEEDBACK_SOURCES, POSSIBLE_FEEDBACKS, FEEDBACK_TYPES
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from configs.definitions import FCL_FREIGHT_CURRENCIES
from fastapi import HTTPException
import datetime
from database.rails_db import *
from micro_services.client import partner, common, maps, spot_search, checkout


class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateFeedback(BaseModel):
    booking_params = BinaryJSONField(null=True)
    cogo_entity_id = UUIDField(index=True,null=True)
    closed_by_id = UUIDField(index=True, null=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)
    created_at = DateTimeField(index=True, default = datetime.datetime.now)
    fcl_freight_rate_id = UUIDField(null=True,index=True)
    feedback_type = CharField(index=True, null=True)
    feedbacks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    outcome = CharField(null=True)
    outcome_object_id = UUIDField(null=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by = BinaryJSONField(null=True)
    performed_by_org_id = UUIDField(index=True, null=True)
    performed_by_org = BinaryJSONField(null=True)
    performed_by_type = CharField(index=True, null=True)
    preferred_detention_free_days = IntegerField(null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    preferred_shipping_line_ids = ArrayField(field_class=UUIDField, null=True, constraints=[SQL("DEFAULT '{}'::uuid[]")])
    preferred_shipping_lines = BinaryJSONField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=TextField, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_feedback_serial_id_seq'::regclass)")])
    source = CharField(index=True, null=True)
    source_id = UUIDField(index=True, null=True)
    status = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    validity_id = UUIDField(index=True, null=True)
    origin_port_id = UUIDField(index=True,null=True)

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateFeedback, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_feedbacks'


    def validate_source(self):
        if self.source and self.source in FEEDBACK_SOURCES:
            return True
        return False

    def validate_source_id(self):
        if self.source == 'spot_search':
            spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})
            if 'list' in spot_search_data and len(spot_search_data['list']) != 0:
                return True

        if self.source == 'checkout':
            checkout_data = checkout.list_checkouts({'filters':{'id': [str(self.source_id)]}})
            if 'list' in checkout_data and len(checkout_data['list']) != 0:
                return True
        return False

    def validate_fcl_freight_rate_id(self):
        fcl_freight_rate_data = FclFreightRate.get(**{'id' : self.fcl_freight_rate_id})
        if fcl_freight_rate_data:
            return True
        return False

    def validate_performed_by_org_id(self):
        performed_by_org_data = get_organization(id=self.performed_by_org_id)
        if len(performed_by_org_data) > 0 and performed_by_org_data[0]['account_type'] == 'importer_exporter':
            return True
        else:
            return False

    def validate_feedbacks(self):
        for feedback in self.feedbacks:
            if feedback in POSSIBLE_FEEDBACKS:
                return True
            return False


    def validate_preferred_freight_rate_currency(self):
        if not self.preferred_freight_rate_currency:
            return True

        fcl_freight_currencies = FCL_FREIGHT_CURRENCIES

        if self.preferred_freight_rate_currency in fcl_freight_currencies:
            return True
        return False

    def validate_preferred_detention_free_days(self):
        if self.preferred_detention_free_days and int(self.preferred_detention_free_days) >= 0:
            return True
        return False

    def validate_preferred_shipping_line_ids(self):
        if not self.preferred_shipping_line_ids:
            pass

        if self.preferred_shipping_line_ids:
            shipping_lines = get_shipping_line(id=self.preferred_shipping_line_ids)
            shipping_lines_hash = {}
            for sl in shipping_lines:
                shipping_lines_hash[sl["id"]] = sl
            for shipping_line_id in self.preferred_shipping_line_ids:
                if not shipping_line_id in shipping_lines_hash:
                    return False
            self.preferred_shipping_lines = shipping_lines

    def validate_feedback_type(self):
        if self.feedback_type in FEEDBACK_TYPES:
            return True
        return False

    def validate_before_save(self):
        if not self.validate_source():
            raise HTTPException(status_code=422, detail="incorrect source")

        if not self.validate_source_id():
            raise HTTPException(status_code=422, detail="incorrect source id")

        if not self.validate_fcl_freight_rate_id():
            raise HTTPException(status_code=422, detail="incorrect fcl freight rate id")

        if not self.validate_performed_by_org_id():
            raise HTTPException(status_code=422, detail="incorrect performed by org id")

        if len(self.feedbacks) != 0:
            if not self.validate_feedbacks():
                raise HTTPException(status_code=422, detail="incorrect feedbacks")

        if not self.validate_preferred_freight_rate_currency():
            raise HTTPException(status_code=422, detail='invalid currency')

        if self.preferred_detention_free_days:
            if not self.validate_preferred_detention_free_days():
                raise HTTPException(status_code=422, detail="incorrect preferred detention free days")

        if self.preferred_shipping_line_ids:
            if not self.validate_preferred_shipping_line_ids():
                raise HTTPException(status_code=422, detail="incorrect preferred shipping line ids")

        if not self.validate_feedback_type():
            raise HTTPException(status_code=422, detail="incorrect feedback type")

        return True

    def supply_agents_to_notify(self):
        locations_data = FclFreightRate.select(
            FclFreightRate.origin_port_id,
            FclFreightRate.origin_country_id,
            FclFreightRate.origin_continent_id,
            FclFreightRate.origin_trade_id,
            FclFreightRate.destination_port_id,
            FclFreightRate.destination_country_id,
            FclFreightRate.destination_continent_id,
            FclFreightRate.destination_trade_id,
            FclFreightRate.commodity    ##added cuz required in return of this function(missing in ruby)
        ).where(FclFreightRate.id == self.fcl_freight_rate_id).first()

        if locations_data:
            origin_locations = [
                locations_data.origin_port_id,
                locations_data.origin_country_id,
                locations_data.origin_continent_id,
                locations_data.origin_trade_id,
            ]
            origin_locations = [t for t in origin_locations if t is not None]
        else:
            origin_locations = []

        if locations_data:
            destination_locations = [
                locations_data.destination_port_id,
                locations_data.destination_country_id,
                locations_data.destination_continent_id,
                locations_data.destination_trade_id
            ]
            destination_locations = [t for t in destination_locations if t is not None]
        else:
            destination_locations = []

        supply_agents_list = partner.list_partner_user_expertises({
            'filters': {'service_type': 'fcl_freight','status': 'active','origin_location_id': origin_locations,'destination_location_id': destination_locations},
            'pagination_data_required': False,
            'page_limit': MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
        })['list']
        supply_agents_list = list(set(t['partner_user_id'] for t in supply_agents_list))

        supply_agents_user_ids = partner.list_partner_users({   ##############
            'filters': {'id': supply_agents_list},
            'pagination_data_required': False,
            'page_limit': MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
            })['list']
        supply_agents_user_ids = list(set(t['user_id'] for t in supply_agents_user_ids))

        route = maps.list_locations({'filters':{'id': [locations_data.origin_port_id, locations_data.destination_port_id]}})['list']
        route = {t['id']:t['display_name'] for t in route}

        return {
          'user_ids': supply_agents_user_ids,
          'origin_location': route[locations_data.origin_port_id],
          'destination_location': route[locations_data.destination_port_id],
          'commodity': locations_data.commodity
        }

    def send_create_notifications_to_supply_agents(self):
        feedback_info = self.supply_agents_to_notify()

        if feedback_info['commodity_type']:
            commodity = feedback_info['commodity_type'].upper()
        data = {
            'type': 'platform_notification',
            'service': 'fcl_freight_rate',
            'service_id': self.id,
            'template_name': 'freight_rate_disliked',
            'variables': {
                'service_type': 'fcl freight',
                'origin_port': feedback_info['origin_location'],
                'destination_port': feedback_info['destination_location'],
                'details': {"commodity" : commodity} if commodity else ''
            }
        }

        for user_id in feedback_info['user_ids']:
            data['user_id'] = user_id
            # common.create_communication(data)

    def send_closed_notifications_to_sales_agent(self):
        locations_data = FclFreightRate.select(
            FclFreightRate.origin_port_id,
            FclFreightRate.origin_country_id,
            FclFreightRate.origin_continent_id,
            FclFreightRate.origin_trade_id,
            FclFreightRate.destination_port_id,
            FclFreightRate.destination_country_id,
            FclFreightRate.destination_continent_id,
            FclFreightRate.destination_trade_id
            ).where(FclFreightRate.id == self.fcl_freight_rate_id).first()#.limit(1)

        # for item in loc_data:
        #     locations_data = model_to_dict(item)
        location_pair_name = maps.list_locations({'filters':{'id': [locations_data['origin_port_id'], locations_data['destination_port_id']]}})['list']
        location_pair_name = {t['id']:t['display_name'] for t in location_pair_name}

        try:
            importer_exporter_id = spot_search.get_spot_search({'id': self.source_id})['detail']['importer_exporter_id']
        except:
            importer_exporter_id = None

        data = {
            'user_id': self.performed_by_id,
            'type': 'platform_notification',
            'service': 'fcl_freight_rate',
            'service_id': self.id,
            'template_name': 'freight_rate_feedback_completed_notification' if ('rate_added' in self.closing_remarks) else 'freight_rate_feedback_closed_notification',
            'variables': {
                'service_type': 'fcl freight',
                'origin_location': location_pair_name[locations_data['origin_port_id']],
                'destination_location': location_pair_name[locations_data['destination_port_id']],
                'remarks': None if ('rate_added' in self.closing_remarks)  else f"Reason: {self.closing_remarks[0].lower().replace('_', ' ')}",
                'request_serial_id': self.serial_id,
                'spot_search_id': self.source_id,
                'importer_exporter_id': importer_exporter_id
            }
        }
        # common.create_communication(data)
