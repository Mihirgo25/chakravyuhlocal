from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from rails_client import client
from fastapi import HTTPException
from configs.fcl_freight_rate_constants import REQUEST_SOURCES
import datetime
from configs.global_constants import PROD_DATA_OPERATIONS_ASSOCIATE_ROLE_ID
from libs.locations import list_locations

class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateLocalRequest(BaseModel):
    booking_params = BinaryJSONField(null=True)
    cargo_readiness_date = DateField(null=True)
    closed_by_id = UUIDField(null=True)
    closed_by = BinaryJSONField(null=True)
    closing_remarks = ArrayField(field_class=CharField, null=True)
    commodity = CharField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    main_port_id = UUIDField(null=True)
    performed_by_id = UUIDField(null=True)
    performed_by = BinaryJSONField(null=True)
    performed_by_org_id = UUIDField(null=True)
    performed_by_type = CharField(null=True)
    port_id = UUIDField(null=True)
    port = BinaryJSONField(null=True)
    preferred_detention_free_days = IntegerField(null=True)
    preferred_rate = DoubleField(null=True)
    preferred_rate_currency = CharField(null=True)
    preferred_shipping_line_ids = ArrayField(field_class=UUIDField, null=True)
    preferred_shipping_line_id = BinaryJSONField(null=True)
    remarks = ArrayField(field_class=CharField, null=True)
    serial_id = BigIntegerField(constraints=[SQL("DEFAULT nextval('fcl_freight_rate_local_requests_serial_id_seq'::regclass)")])
    shipping_line_id = UUIDField(null=True)
    shipping_line_detail = BinaryJSONField(null=True)
    source = CharField(null=True)
    source_id = UUIDField(null=True)
    spot_search = BinaryJSONField(null=True)
    status = CharField(null=True)
    trade_id = UUIDField(null=True)
    trade_type = CharField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateLocalRequest, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_freight_rate_local_requests'

    def validate_source(self):
        if self.source and self.source in REQUEST_SOURCES:
            return True
        return False
    
    def validate_source_id(self):
        if self.source == 'spot_search':
            spot_search_data = client.ruby.list_spot_searches({'filters': {'id': [str(self.source_id)]}})
            if 'list' in spot_search_data and len(spot_search_data['list']) != 0:
                return True
            return False

    def validate_performed_by_id(self):
        data = client.ruby.get_users({'id': str(self.performed_by_id)})
        if data!={}:
            return True  
        else:
            return False

    def validate_performed_by_org_id(self):
        performed_by_org_data = client.ruby.list_organizations({'filters':{'id': [str(self.performed_by_org_id)]}})['list']
        if len(performed_by_org_data) != 0 and performed_by_org_data[0]['account_type'] == 'importer_exporter':
            return True
        return False

    def validate_closed_by_id(self):
        if not self.closed_by_id:
            return True

        data = client.ruby.get_users({'id': str(self.closed_by_id)})
        if data!={}:
            return True       
        else:
            return False

    def validate(self):
        if not self.validate_source():
            raise HTTPException(status_code=404, detail="incorrect source")

        if not self.validate_source_id():
            raise HTTPException(status_code=404, detail="invalid source id")
        
        if not self.validate_performed_by_id():
            raise HTTPException(status_code=404, detail='Invalid Performed by ID')
    
        if not self.validate_performed_by_org_id():
            raise HTTPException(status_code=404, detail="incorrect performed by id")

        if not self.validate_closed_by_id():
            raise HTTPException(status_code=404, detail='Invalid Closed by ID')
        return True

    def send_closed_notifications_to_sales_agent(self):
        location_pair = FclFreightRateLocalRequest.select(FclFreightRateLocalRequest.port_id).where(FclFreightRateLocalRequest.source_id == self.source_id).limit(1).dicts().get()
        location_pair_data = list_locations({ 'id': [location_pair['origin_port_id'], location_pair['destination_port_id']] })['list']
        location_pair_name = {data['id']:data['display_name'] for data in location_pair_data}
        try:
            importer_exporter_id = client.ruby.get_spot_search({'id': self.source_id})['detail']['importer_exporter_id']
        except:
            importer_exporter_id = None
        data = {
        'user_id': self.performed_by_id,
        'type': 'platform_notification',
        'service': 'fcl_freight_rate_locals',
        'service_id': self.id,
        'template_name': 'missing_customs_rate_request_completed_notification' if 'rate_added' in self.closing_remarks else 'missing_customs_rate_request_closed_notification',
        'variables': { 'service_type': 'fcl freight local',
                    'location': location_pair_name[location_pair['port_id']],
                    'remarks': None if 'rate_added' in self.closing_remarks else "Reason: {}.".format(self.closing_remarks[0].lower().replace('_', ' ')),
                    'request_serial_id': self.serial_id,
                    'spot_search_id': self.source_id,
                    'importer_exporter_id': importer_exporter_id }

        }
        client.ruby.create_communication(data)
    

    def send_notifications_to_supply_agents(self):
        port = list_locations({'id': self.port_id})['list'][0]['display_name']
        try:
            user_ids = [item['user_id'] for item in client.ruby.list_partner_users({'filters':{'role_ids':PROD_DATA_OPERATIONS_ASSOCIATE_ROLE_ID, 'status':'active','partner_status':'active'}})['list']]
        except:
            user_ids = None
       
        data = {
        'type': 'platform_notification',
        'service': 'spot_search',
        'service_id': self.source_id,
        'template_name': 'missing_locals_rate_request_notification',
        'variables': { 'service_type': 'fcl local',
                    'location': port,
                    'request_serial_id' : self.serial_id }
        }
        for user_id in user_ids:
            data['user_id'] = user_id
            client.ruby.create_communication(data)