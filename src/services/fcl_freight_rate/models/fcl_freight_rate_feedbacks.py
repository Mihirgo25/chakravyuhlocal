
from peewee import *
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import FEEDBACK_SOURCES,POSSIBLE_FEEDBACKS,FEEDBACK_TYPES
from configs.defintions import FCL_FREIGHT_CURRENCIES
import yaml
from rails_client import client
from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from src.configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

class FclFreightRateFeedback(BaseModel):
    booking_params = BinaryJSONField(null=True)
    closed_by_id = UUIDField(null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::character varying[]")], field_class=CharField, null=True)
    created_at = DateTimeField()
    fcl_freight_rate_id = UUIDField(null=True)
    feedback_type = CharField(null=True)
    feedbacks = ArrayField(field_class=CharField, null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    outcome = CharField(null=True)
    outcome_object_id = UUIDField(null=True)
    performed_by_id = UUIDField(null=True)
    performed_by_org_id = UUIDField(null=True)
    performed_by_type = CharField(null=True)
    preferred_detention_free_days = IntegerField(null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    preferred_shipping_line_ids = ArrayField(field_class=UUIDField, null=True)
    remarks = ArrayField(field_class=CharField, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_feedbacks_serial_id_seq'::regclass)")])
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    status = CharField(null=True)
    updated_at = DateTimeField()
    validity_id = UUIDField(null=True)

    class Meta:
        table_name = 'fcl_freight_rate_feedbacks'   

    def validate_source(self):
        if self.source not in FEEDBACK_SOURCES:
            return False
        return True

    def validate_source_id(self):
        if self.source =='spot_search':
            data=client.ruby.list_spot_searches({'filters':{'id':self.source_id}})["list"]
        elif self.source =='checkout':
            data  = client.ruby.list_checkouts({'filters':{'id':self.source_id}})["list"]
        if len(data)==0:
            return False
        return True
    
    def validate_fcl_freight_rate_id(self):
        data = FclFreightRate.select().where(id = self.fcl_freight_rate_id)

        if not data:
            return False
        return True

    def validate_performed_by_id(self):
        data = client.ruby.list_users({'filters':{'id':self.performed_by_id}})["list"]

        if len(data)==0:
            return False
        return True

    def validate_performed_by_org_id(self):
        data = client.ruby.list_organizations({'filters':{'id':self.performed_by_org_id}})

        if len(data)==0:
            return False
        
        return True
    
    def validate_feedbacks(self):
        for feedback in self.feedbacks:
            if feedback not in POSSIBLE_FEEDBACKS:
                return False
        return True

    def validate_preferred_freight_rate_currency(self):

        if not self.preferred_freight_rate_currency:
            return True
        with open(FCL_FREIGHT_CURRENCIES, 'r') as file:
            fcl_freight_currencies = yaml.safe_load(file)
        

        if self.preferred_freight_rate_currency not in fcl_freight_currencies:
            return False
        return True
    
    def validate_preferred_detention_free_days(self):
        if not self.preferred_detention_free_days:
            return True
        
        if self.preferred_detention_free_days < 0 :
            return False
        return True

    def validate_preferred_shipping_line_ids(self):

        data = client.ruby.list_operators({'filters':{'id':self.preferred_shipping_line_ids,'operator_type':'shipping_line'}})

        if len(data)==0:
            return False
        return True
    
    def validate_feedback_type(self):
        if self.feedback_type not in FEEDBACK_TYPES:
            return False
        return True
    
    # validate as many

    def supply_agents_to_notify(self):
        locations_data = FclFreightRate.select(FclFreightRate.origin_port_id,FclFreightRate.origin_country_id,
        FclFreightRate.origin_continent_id,FclFreightRate.origin_trade_id,FclFreightRate.destination_port_id,
        FclFreightRate.destination_country_id,FclFreightRate.destination_continent_id,FclFreightRate.destination_trade_id).first()

        origin_locations = {
            "origin_port_id": locations_data.origin_port_id,
            "origin_country_id":locations_data.origin_country_id,
            "origin_continent_id":locations_data.origin_continent_id,
            "origin_trade_id":locations_data.origin_trade_id
        }

        destination_locations = {
            "destination_port_id": locations_data.destination_port_id,
            "destination_country_id":locations_data.destination_country_id,
            "destination_continent_id":locations_data.destination_continent_id,
            "destination_trade_id":locations_data.destination_trade_id
        }

        supply_agents_list = client.ruby.list_patner_user_expertises({
        "filters": {
        "service_type": 'fcl_freight',
        "status": 'active',
        "origin_location_id": origin_locations,
        "destination_location_id": destination_locations
        },
        "pagination_data_required": False,
        "page_limit": MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
        })['list']
        supply_agents_list = list(map(lambda x: x["partner_user_id"], supply_agents_list))

        supply_agents_user_ids = client.ruby.list_partner_users({"filters": {
            "id": supply_agents_list
        },
        "pagination_data_required": False,
        "page_limit":MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT})['list']

        supply_agents_user_ids = list(map(lambda x: x["user_id"], supply_agents_user_ids))

        route = client.ruby.list_locations({"filters": {
        id: {locations_data["origin_port_id"], locations_data["destination_port_id"]}}})['list']

        route = dict(map(lambda x: (x['id',x['display_name']]),route))

        return {
            "users_ids" : supply_agents_user_ids,
            "origin_location": route[locations_data["origin_port_id"]],
            "destination_location":route[locations_data["destination_port_id"]],
            # "commodity": route["commodity"] incomplete

        }

    def send_create_notifications_to_supply_agents(self):
        feedback_info = self.supply_agents_to_notify()
        # commodity = feedback_info[:commodity_type].upcase if feedback_info[:commodity_type].present? 
        data = {
            "type": 'platform_notification',
            "service": 'fcl_freight_rate',
      "service_id": self.id,
      "template_name": 'freight_rate_disliked',
      "variables": {
        "service_type": 'fcl freight',
        "origin_port": feedback_info["origin_location"],
        "destination_port": feedback_info["destination_location"],
        "details":''
        # details: commodity.present? ? "commodity : #{commodity}" : ''
        } 
        }
        for user_id in feedback_info['user_ids']:
            data['user_id'] = user_id
            client.ruby.create_communication(data)

    def send_closed_notifications_to_sales_agent(self):
        locations_data = FclFreightRate.select(FclFreightRate.origin_port_id,FclFreightRate.origin_country_id,
        FclFreightRate.origin_continent_id,FclFreightRate.origin_trade_id,FclFreightRate.destination_port_id,
        FclFreightRate.destination_country_id,FclFreightRate.destination_continent_id,FclFreightRate.destination_trade_id).first()

        location_pair_name = client.ruby.list_locations({"filters": {
        {id: {locations_data["origin_port_id"], locations_data["destination_port_id"]}
        }}})['list']

        location_pair_name = dict(map(lambda x: (x['id',x['display_name']]),location_pair_name))

        importer_exporter_id = client.ruby.get_spot_search({'id': self.source_id})['detail']['importer_exporter_id']

        data ={
            "user_id" : self.performed_by_id,
            "type" : 'platform_notification',
            "service" : 'fcl_freight_rate',
            'service_id' : self.id,
            'template_name' : "freight_rate_feedback_completed_notification" if 'rate_added' in self.closing_remarks else "freight_rate_feedback_closed_notification",
            'variables':{
                'service_type': 'fcl freight',
                'origin_location' : location_pair_name[locations_data['origin_port_id']],
                'destination_location': location_pair_name[locations_data["destination_port_id"]],
                'remarks' : None if 'rate_added' in self.closing_remarks else f"Reason: {self.closing_remarks[0].lower().replace('_',' ')}",
                'request_serial_id':self.serial_id,
                'spot_search_id':self.source_id,
                'importer_exporter_id':importer_exporter_id

            }
        }
        client.ruby.create_communication(data)










        
        

        

    