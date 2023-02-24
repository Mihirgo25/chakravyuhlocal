from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from configs.fcl_freight_rate_constants import TRADE_TYPES
from rails_client import client
from services.fcl_freight_rate.models.fcl_freight_rates import FclFreightRate
from playhouse.shortcuts import model_to_dict

class BaseModel(Model):
    class Meta:
        database = db


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

    def supply_agents_to_notify
    locations_data = FclFreightRate.where(id: self.fcl_freight_rate_id).select(
      :origin_port_id,
      :origin_country_id,
      :origin_continent_id,
      :origin_trade_id,
      :destination_port_id,
      :destination_country_id,
      :destination_continent_id,
      :destination_trade_id
    ).first

    origin_locations = locations_data.slice(
      :origin_port_id,
      :origin_country_id,
      :origin_continent_id,
      :origin_trade_id
    ).values.compact

    destination_locations = locations_data.slice(
      :destination_port_id,
      :destination_country_id,
      :destination_continent_id,
      :destination_trade_id
    ).values.compact

    supply_agents_list = ListPartnerUserExpertises.run!({
      filters: {
        service_type: 'fcl_freight',
        status: 'active',
        origin_location_id: origin_locations,
        destination_location_id: destination_locations
      },
      pagination_data_required: false,
      page_limit: ::GlobalConstants::MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
    })[:list].pluck(:partner_user_id).uniq

    supply_agents_user_ids = ListPartnerUsers.run!({
      filters: {
        id: supply_agents_list
      },
      pagination_data_required: false,
      page_limit: ::GlobalConstants::MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
    })[:list].pluck(:user_id).uniq

    route = ListLocations.run!({
      filters: {
        id: locations_data.slice(:origin_port_id, :destination_port_id).values
      }
    })[:list].pluck(:id, :display_name).to_h

    # return {
    #   user_ids: supply_agents_user_ids,
    #   origin_location: route[locations_data[:origin_port_id]],
    #   destination_location: route[locations_data[:destination_port_id]],
    #   commodity: route[:commodity]
    # }
    
    def send_create_notifications_to_supply_agents(self):
        feedback_info = supply_agents_to_notify()
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
            data[:user_id] = user_id
            client.ruby.create_communication(data)

    def send_closed_notifications_to_sales_agent(self):
        loc_data = FclFreightRate.select(
            FclFreightRate.origin_port_id,
            FclFreightRate.origin_country_id,
            FclFreightRate.origin_continent_id,
            FclFreightRate.origin_trade_id,
            FclFreightRate.destination_port_id,
            FclFreightRate.destination_country_id,
            FclFreightRate.destination_continent_id,
            FclFreightRate.destination_trade_id
            ).where(FclFreightRate.id == self.fcl_freight_rate_id).limit(1)
         
        for item in loc_data:
            locations_data = model_to_dict(item)

        location_pair_name = client.ruby.list_locations({
        'filters': {
            'id': [locations_data['origin_port_id'], locations_data['destination_port_id']]
        }
        })['list']
        pluck(:id, :display_name).to_h
        
        try:
            importer_exporter_id = client.ruby.get_spot_search({'id': self.source_id})['detail']['importer_exporter_id'] 
        except:
            importer_exporter_id = None

        data = {
            'user_id': self.performed_by_id,
            'type': 'platform_notification',
            'service': 'fcl_freight_rate',
            'service_id': self.id,
            'template_name': (self.closing_remarks.include? 'rate_added') ? 'freight_rate_feedback_completed_notification' : 'freight_rate_feedback_closed_notification',
            'variables': {
                'service_type': 'fcl freight',
                'origin_location': location_pair_name[locations_data['origin_port_id']],
                'destination_location': location_pair_name[locations_data['destination_port_id']],
                'remarks': (closing_remarks.include? 'rate_added') ? nil : "Reason: #{closing_remarks.first.downcase.tr('_', ' ')}",
                'request_serial_id': self.serial_id,
                'spot_search_id': self.source_id,
                'importer_exporter_id': importer_exporter_id
            }.compact
            }
        client.ruby.create_communication(data)

#   belongs_to :rates, class_name: 'FclFreightRate', foreign_key: 'fcl_freight_rate_id'

#   validates :source, inclusion: { in: FclFreightRateConstants::FEEDBACK_SOURCES }

#   validates :source_id, service_object: { object: 'spot_search' }, if: Proc.new { |t| t[:source] == 'spot_search' }

#   validates :source_id, service_object: { object: 'checkout' }, if: Proc.new { |t| t[:source] == 'checkout' }

#   validates :fcl_freight_rate_id, service_object: { object: 'fcl_freight_rate' }

#   validates :performed_by_id, service_object: { object: 'user' }

#   validates :performed_by_org_id, service_object: { object: 'organization', filters: { account_type: 'importer_exporter' } }

#   validates :feedbacks, array_obj_inclusion: { inclusion_values: Proc.new { |_t| FclFreightRateConstants::POSSIBLE_FEEDBACKS } }

#   validates :preferred_freight_rate_currency, currency: true, allow_blank: true

#   validates :preferred_detention_free_days, numericality: { greater_than_or_equal_to: 0 }, allow_blank: true

#   validates :preferred_shipping_line_ids, service_object: { object: 'operator', filters: { operator_type: 'shipping_line' } }, allow_blank: true

#   validates :feedback_type, inclusion: { in: FclFreightRateConstants::FEEDBACK_TYPES }

#   has_many :audits, class_name: :FclFreightRateAudit, as: :object

