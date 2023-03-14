from peewee import *
from database.db_session import db 
import datetime
from rails_client import client
from configs.global_constants import CONTAINER_SIZES,CONTAINER_TYPES
from configs.fcl_freight_rate_constants import FREIGHT_CONTAINER_COMMODITY_MAPPINGS
class BaseModel(Model):
    class Meta:
        database = db

class FreightTrendRate(BaseModel):
    id = UUIDField(primary_key=True,constraints=[SQL("DEFAULT gen_random_uuid()")])
    origin_port_id = UUIDField(null=True)
    destination_port_id = UUIDField(null=True)
    commodity = TextField(null=True)
    price = FloatField(null=True)
    validity_start = DateTimeField(null = True)
    validity_end = DateTimeField(null =True)
    organization_id = UUIDField(null=True)
    volume = FloatField(null=True)
    currency = TextField(null=True)
    final_price = FloatField(null=True)
    shipping_line_id = UUIDField(null= True)
    container_size = TextField(null= True)
    container_type = TextField(null= True)
    source = TextField(null= True)
    created_at = DateTimeField(default = datetime.datetime.now())
    updated_at = DateTimeField(default = datetime.datetime.now())

    class Meta:
        table_name = 'freight_trend_rates'

    

    def validations(self):
        obj = {"filters" : {"id": [str(self.origin_port_id), str(self.destination_port_id)],'type':'seaport'}}
        port_ids = client.ruby.list_locations(obj)['list']

        if len(port_ids)!=2:
            return False

        obj = {"filters":{"id":self.shipping_line_id,'operator_type':'shipping_line'}}
        shipping_line_id = client.ruby.list_operators(obj)['list']

        if len(shipping_line_id)!=1:
            return False
        
        if not self.currency:
            return False

        if self.organization_id:
            obj =  {"filters":{"id":self.organization_id}}
            organization_id = client.ruby.list_organizations(obj)['list']

            if len(organization_id)!=1:
                return False
        
        if self.container_size not in CONTAINER_SIZES:
            return False
        
        if self.container_type not in CONTAINER_TYPES:
            return False
        
        if self.commodity not in FREIGHT_CONTAINER_COMMODITY_MAPPINGS[self.container_type]:
            return False
        
        if self.source not in ['cogoport']:
            return False
        
        if self.volume:
            if not isinstance(self.volume,(int,float)) and self.volume>0:
                return False
    

    def detail(self,currency):
        detail = vars(self)
        detail['currecny'] = currency
        detail['price'] = self.price if self.currency==currency else client.ruby.get_money_exchange_for_fcl({'price':self.price,'from_currency':self.currency,'to_currency':currency})['price']

        return detail

        

        

        

