from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from fastapi import HTTPException
import datetime
from micro_services.client import *
from database.rails_db import *

class BaseModel(Model):
    # db.execute_sql('create sequence fcl_freight_rate_requests_serial_id_seq')
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateRequest(BaseModel):
    booking_params = BinaryJSONField(null=True)
    cargo_readiness_date = DateTimeField(null=True)
    cargo_weight_per_container = IntegerField(null=True)
    cogo_entity_id = UUIDField(index=True, null = True)
    closed_by_id = UUIDField(index=True, null=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    commodity = CharField(index=True, null=True)
    container_size = CharField(index=True, null=True)
    container_type = CharField(index=True, null=True)
    containers_count = IntegerField(null=True)
    created_at = DateTimeField(index=True, default = datetime.datetime.now)
    destination_continent_id = UUIDField( null=True)
    destination_country_id = UUIDField( null=True)
    destination_port_id = UUIDField(index=True, null=True)
    destination_port = BinaryJSONField(null=True)
    destination_trade_id = UUIDField( null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    inco_term = CharField(index=True, null=True)
    origin_continent_id = UUIDField( null=True)
    origin_country_id = UUIDField( null=True)
    origin_port_id = UUIDField(index=True, null=True)
    origin_port = BinaryJSONField(null=True)
    origin_trade_id = UUIDField( null=True)
    performed_by_id = UUIDField(index=True, null=True)
    performed_by = BinaryJSONField(null=True)
    performed_by_org_id = UUIDField(index=True, null=True)
    performed_by_type = CharField(index=True, null=True)
    preferred_detention_free_days = IntegerField(null=True)
    preferred_freight_rate = DoubleField(null=True)
    preferred_freight_rate_currency = CharField(null=True)
    preferred_shipping_line_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    preferred_shipping_lines = BinaryJSONField(null=True)
    preferred_storage_free_days = IntegerField(null=True)
    remarks = ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    request_type = CharField(null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_request_serial_id_seq'::regclass)")])
    source = CharField( null=True)
    source_id = UUIDField(index=True ,null=True)
    status = CharField(index=True, null=True)
    updated_at = DateTimeField(default = datetime.datetime.now)
    attachment_file_urls=ArrayField(constraints=[SQL("DEFAULT '{}'::text[]")], field_class=TextField, null=True)
    commodity_description = TextField(null=True)
    reverted_rates_count = IntegerField(null=True)
    reverted_by_user_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    expiration_time = DateTimeField(null = True)
    relevant_supply_agent_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    reverted_rates = BinaryJSONField(null=True)

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateRequest, self).save(*args, **kwargs)

    def refresh(self):
        return type(self).get(self._pk_expr())

    class Meta:
        table_name = 'fcl_freight_rate_requests'

    # def validate_source(self):
    #     if self.source and self.source not in REQUEST_SOURCES:
    #         raise HTTPException(status_code=400, detail="Invalid source")


    # def validate_source_id(self):
    #     if self.source == 'spot_search':
    #         spot_search_data = spot_search.list_spot_searches({'filters': {'id': [str(self.source_id)]}})['list']
    #         if len(spot_search_data) == 0:
    #             raise HTTPException(status_code=400, detail="Invalid Source ID")

    # def validate_performed_by_id(self):
    #     data = get_user(self.performed_by_id)

    #     if data!={}:
    #         pass
    #     else:
    #         raise HTTPException(status_code=400, detail='Invalid Performed by ID')

    # def validate_performed_by_org_id(self):
    #     performed_by_org_data = get_organization(id=str(self.performed_by_org_id))
    #     if len(performed_by_org_data) == 0 or performed_by_org_data[0]['account_type'] != 'importer_exporter':
    #         raise HTTPException(status_code=400, detail='Invalid Account Type')

    def validate_preferred_shipping_line_ids(self):
        if not self.preferred_shipping_line_ids:
            pass
        if self.preferred_shipping_line_ids:
            # preferred_shipping_lines = []
            # for shipping_line_id in self.preferred_shipping_line_ids:
            shipping_line_data = get_operators(id=self.preferred_shipping_line_ids)
            if len(shipping_line_data) != len(self.preferred_shipping_line_ids):
                raise HTTPException(status_code=400, detail='Invalid Shipping Line ID')
            self.preferred_shipping_lines = shipping_line_data
            self.preferred_shipping_line_ids = [uuid.UUID(str(shipping_line_id)) for shipping_line_id in self.preferred_shipping_line_ids]
            # preferred_shipping_lines.append(shipping_line_data[0])

    def set_location(self):
        location_data = maps.list_locations({'filters':{'id':[self.origin_port_id,self.destination_port_id]}})['list']
        for location in location_data:
            if location['id']==self.origin_port_id:
                self.origin_port = {key:value for key,value in location.items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}
            elif location['id']==self.destination_port_id:
                self.destination_port = {key:value for key,value in location.items() if key in ['id', 'name', 'display_name', 'port_code', 'type']}

    def validate(self):
        # self.validate_source()
        # self.validate_source_id()
        # self.validate_performed_by_id()
        # self.validate_performed_by_org_id()
        self.validate_preferred_shipping_line_ids()
        return True


    def send_closed_notifications_to_sales_agent(self):
        location_pair = FclFreightRateRequest.select(FclFreightRateRequest.origin_port_id, FclFreightRateRequest.destination_port_id).where(FclFreightRateRequest.source_id == self.source_id).limit(1).dicts().get()
        location_pair_data = maps.list_locations({ 'filters': {'id': [str(location_pair['origin_port_id']), str(location_pair['destination_port_id'])] }})['list']
        location_pair_name = {data['id']:data['display_name'] for data in location_pair_data}
        try:
            importer_exporter_id = spot_search.get_spot_search({'id': str(self.source_id)})['detail']['importer_exporter_id']
        except:
            importer_exporter_id = None
        origin_location = location_pair_name[str(location_pair['origin_port_id'])]
        destination_location = location_pair_name[str(location_pair['destination_port_id'])]
        data = {
            'user_id': self.performed_by_id,
            'type': 'platform_notification',
            'service': 'fcl_freight_rate',
            'service_id': self.id,
            'template_name': 'freight_rate_request_completed_notification' if 'rate_added' in self.closing_remarks else 'freight_rate_request_closed_notification',
            'variables': { 
                'service_type': 'fcl freight',
                'origin_location': origin_location,
                'destination_location': destination_location,
                'remarks': None if 'rate_added' in self.closing_remarks else "Reason: {}.".format(self.closing_remarks[0].lower().replace('_', ' ')),
                'request_serial_id': str(self.serial_id),
                'spot_search_id': str(self.source_id),
                'importer_exporter_id': importer_exporter_id 
            }
        }

        if 'rate_added' in self.closing_remarks:
            subject = 'Freight Rate Request Completed'
            body = f"Rate has been added for Request No: {str(self.serial_id)}, fcl freight from {origin_location} to {destination_location}."
        else:
            subject = 'Freight Rate Request Closed'
            remarks = f"Reason: {self.closing_remarks[0].lower().replace('_', ' ')}."
            body = f"Your rate request has been closed for Request No: {str(self.serial_id)}, fcl freight from {origin_location} to {destination_location}. {remarks}"

        push_notification_data = {
        'type': 'push_notification',
        'service': 'fcl_freight_rate',
        'service_id': str(self.id),
        'provider_name': 'firebase',
        'template_name': 'push_notification',
        'user_id': str(self.performed_by_id),
        'variables': {
            'subject': subject,
            'body': body,
            'notification_source': 'spot_search',
            'notification_source_id': str(self.source_id)
            }
        }

        common.create_communication(push_notification_data)
        common.create_communication(data) 

    def send_closed_notifications_to_user(self):
        params={
            'spot_search_id': str(self.source_id),
            'update_to_id': str(self.performed_by_id),
            'update_to_type': self.performed_by_type
        }
        
        spot_search.send_spot_search_rate_update(params)

        