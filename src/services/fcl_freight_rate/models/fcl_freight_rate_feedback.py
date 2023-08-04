from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from fastapi import HTTPException
import datetime
from database.rails_db import *
from micro_services.client import common, maps, spot_search
from configs.fcl_freight_rate_constants import RATE_FEEDBACK_RELEVANT_ROLE_ID

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
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    created_at = DateTimeField(index=True, default = datetime.datetime.now)
    fcl_freight_rate_id = UUIDField(null=True,index=True)
    feedback_type = CharField(index=True, null=True)
    feedbacks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
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
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_feedback_serial_id_seq'::regclass)")])
    source = CharField(index=True, null=True)
    source_id = UUIDField(index=True, null=True)
    status = CharField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    validity_id = UUIDField(index=True, null=True)
    origin_port_id = UUIDField(index=True,null=True)
    origin_continent_id  = UUIDField(null=True)
    origin_trade_id = UUIDField(null=True)
    origin_country_id = UUIDField(null=True)
    destination_port_id = UUIDField(index=True,null=True)
    destination_continent_id  = UUIDField(null=True)
    destination_trade_id = UUIDField(null=True)
    destination_country_id = UUIDField(null=True)
    commodity = CharField(null=True)
    container_size=CharField(null=True)
    container_type=CharField(null=True)
    service_provider_id= UUIDField(null=True)
    origin_port = BinaryJSONField(null=True)
    destination_port = BinaryJSONField(null=True)
    attachment_file_urls=ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    commodity_description=TextField(null=True)
    relevant_supply_agent_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    reverted_validities = BinaryJSONField(null=True)

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateFeedback, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_feedbacks'
        
        
    def refresh(self):
        return type(self).get(self._pk_expr())


    # def validate_source(self):
    #     if self.source and self.source in FEEDBACK_SOURCES:
    #         return True
    #     return False

    # def validate_source_id(self):
    #     if self.source == 'spot_search':
    #         spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})
    #         if 'list' in spot_search_data and len(spot_search_data['list']) != 0:
    #             return True

    #     if self.source == 'checkout':
    #         checkout_data = checkout.list_checkouts({'filters':{'id': [str(self.source_id)]}})
    #         if 'list' in checkout_data and len(checkout_data['list']) != 0:
    #             return True
    #     return False

    # def validate_fcl_freight_rate_id(self):
    #     fcl_freight_rate_data = FclFreightRate.get(**{'id' : self.fcl_freight_rate_id})
    #     if fcl_freight_rate_data:
    #         return True
    #     return False

    # def validate_performed_by_org_id(self):
    #     performed_by_org_data = get_organization(id=self.performed_by_org_id)
    #     if len(performed_by_org_data) > 0 and performed_by_org_data[0]['account_type'] == 'importer_exporter':
    #         return True
    #     else:
    #         return False

    # def validate_feedbacks(self):
    #     for feedback in self.feedbacks:
    #         if feedback in POSSIBLE_FEEDBACKS:
    #             return True
    #         return False


    # def validate_preferred_freight_rate_currency(self):
    #     if not self.preferred_freight_rate_currency:
    #         return True

    #     fcl_freight_currencies = FCL_FREIGHT_CURRENCIES

    #     if self.preferred_freight_rate_currency in fcl_freight_currencies:
    #         return True
    #     return False

    # def validate_preferred_detention_free_days(self):
    #     if self.preferred_detention_free_days and int(self.preferred_detention_free_days) >= 0:
    #         return True
    #     return False

    def validate_preferred_shipping_line_ids(self):
        if not self.preferred_shipping_line_ids:
            return True

        if self.preferred_shipping_line_ids:
            ids = []
            for sl_id in self.preferred_shipping_line_ids:
                ids.append(str(sl_id))
            
            shipping_lines = get_operators(id=ids)
            shipping_lines_hash = {}
            for sl in shipping_lines:
                shipping_lines_hash[sl["id"]] = sl
            for shipping_line_id in self.preferred_shipping_line_ids:
                if not str(shipping_line_id) in shipping_lines_hash:
                    return False
            self.preferred_shipping_lines = shipping_lines
        return True

    # def validate_feedback_type(self):
    #     if self.feedback_type in FEEDBACK_TYPES:
    #         return True
    #     return False

    def validate_before_save(self):
        # if not self.validate_source():
        #     raise HTTPException(status_code=400, detail="incorrect source")

        # if not self.validate_source_id():
        #     raise HTTPException(status_code=400, detail="incorrect source id")

        # if not self.validate_fcl_freight_rate_id():
        #     raise HTTPException(status_code=400, detail="incorrect fcl freight rate id")

        # if not self.validate_performed_by_org_id():
        #     raise HTTPException(status_code=400, detail="incorrect performed by org id")

        # if len(self.feedbacks) != 0:
        #     if not self.validate_feedbacks():
        #         raise HTTPException(status_code=400, detail="incorrect feedbacks")

        # if not self.validate_preferred_freight_rate_currency():
        #     raise HTTPException(status_code=400, detail='invalid currency')

        # if self.preferred_detention_free_days:
        #     if not self.validate_preferred_detention_free_days():
        #         raise HTTPException(status_code=400, detail="incorrect preferred detention free days")

        if self.preferred_shipping_line_ids:
            if not self.validate_preferred_shipping_line_ids():
                raise HTTPException(status_code=400, detail="incorrect preferred shipping line ids")

        # if not self.validate_feedback_type():
        #     raise HTTPException(status_code=400, detail="incorrect feedback type")

        return True

    def get_relevant_supply_agents(self, service, origin_locations, destination_locations):
        supply_agents_list = get_partner_users_by_expertise(service, origin_locations, destination_locations)
        supply_agents_list = list(set(t['partner_user_id'] for t in supply_agents_list))

        supply_agents_user_ids = get_partner_users(supply_agents_list, role_ids= list(RATE_FEEDBACK_RELEVANT_ROLE_ID.values()))

        supply_agents_user_ids = list(set(t['user_id'] for t in supply_agents_user_ids))

        return supply_agents_user_ids

    def send_create_notifications_to_supply_agents(self, supply_agent_notification_params):
        feedback_info = supply_agent_notification_params
        commodity = ''
        if 'commodity_type' in feedback_info and feedback_info['commodity_type']:
            commodity = feedback_info['commodity_type'].upper()
        origin_port = feedback_info['origin_location']
        destination_port = feedback_info['destination_location']
        data = {
            'type': 'platform_notification',
            'service': 'fcl_freight_rate',
            'service_id': str(self.id),
            'template_name': 'freight_rate_disliked',
            'variables': {
                'service_type': 'fcl freight',
                'origin_port': origin_port,
                'destination_port': destination_port,
                'details': {"commodity" : commodity}
            }
        }

        for user_id in feedback_info['user_ids']:
            data['user_id'] = user_id
            common.create_communication(data)

    def set_relevant_supply_agents(self, request):
        from services.fcl_freight_rate.interaction.update_fcl_freight_rate_feedback import update_fcl_freight_rate_feedback

        locations_data = FclFreightRate.select(
            FclFreightRate.origin_port_id,
            FclFreightRate.origin_country_id,
            FclFreightRate.origin_continent_id,
            FclFreightRate.origin_trade_id,
            FclFreightRate.destination_port_id,
            FclFreightRate.destination_country_id,
            FclFreightRate.destination_continent_id,
            FclFreightRate.destination_trade_id,
            FclFreightRate.commodity,
        ).where(FclFreightRate.id == self.fcl_freight_rate_id).first()

        if locations_data:
            origin_locations = [
                str(locations_data.origin_port_id),
                str(locations_data.origin_country_id),
                str(locations_data.origin_continent_id),
                str(locations_data.origin_trade_id),
            ]
            origin_locations = [t for t in origin_locations if t is not None]
        else:
            origin_locations = []

        if locations_data:
            destination_locations = [
                str(locations_data.destination_port_id),
                str(locations_data.destination_country_id),
                str(locations_data.destination_continent_id),
                str(locations_data.destination_trade_id)
            ]
            destination_locations = [t for t in destination_locations if t is not None]
        else:
            destination_locations = []

        supply_agents_user_ids = self.get_relevant_supply_agents('fcl_freight', origin_locations, destination_locations)

        update_fcl_freight_rate_feedback({'fcl_freight_rate_feedback_id': self.id, 'relevant_supply_agent_ids': supply_agents_user_ids, 'performed_by_id': request.get('performed_by_id')})

        route = maps.list_locations({'filters':{'id': [str(locations_data.origin_port_id), str(locations_data.destination_port_id)]}})['list']
        route = {t['id']:t['display_name'] for t in route}

        supply_agent_notification_params = {
          'user_ids': supply_agents_user_ids,
          'origin_location': route[str(locations_data.origin_port_id)],
          'destination_location': route[str(locations_data.destination_port_id)],
          'commodity': locations_data.commodity
        }

        self.send_create_notifications_to_supply_agents(supply_agent_notification_params)

        return supply_agents_user_ids


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
        location_pair_name = maps.list_locations({'filters':{'id': [str(locations_data.origin_port_id), str(locations_data.destination_port_id)]}})['list']
        location_pair_name = {t['id']:t['display_name'] for t in location_pair_name}

        try:
            importer_exporter_id = spot_search.get_spot_search({'id': str(self.source_id)})['detail']['importer_exporter_id']
        except:
            importer_exporter_id = None

        origin_location = location_pair_name[str(locations_data.origin_port_id)]
        destination_location = location_pair_name[str(locations_data.destination_port_id)]

        data = {
            'user_id': str(self.performed_by_id),
            'type': 'platform_notification',
            'service': 'fcl_freight_rate',
            'service_id': str(self.id),
            'template_name': 'freight_rate_feedback_completed_notification' if ('rate_added' in self.closing_remarks) else 'freight_rate_feedback_closed_notification',
            'variables': {
                'service_type': 'fcl freight',
                'origin_location': origin_location,
                'destination_location': destination_location,
                'remarks': None if ('rate_added' in self.closing_remarks)  else f"Reason: {self.closing_remarks[0].lower().replace('_', ' ')}",
                'request_serial_id': str(self.serial_id),
                'spot_search_id': str(self.source_id),
                'importer_exporter_id': importer_exporter_id
            }
        }
        common.create_communication(data)
