from database.db_session import db
from peewee import * 
import json
from playhouse.postgres_ext import BinaryJSONField, ArrayField
from micro_services.client import *
from fastapi import HTTPException
from datetime import datetime,timedelta
from database.rails_db import *
from configs.definitions import HAULAGE_FREIGHT_CHARGES
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.haulage_freight_rate.models.haulage_freight_rate_audits import HaulageFreightRateAudit

ACTION_NAMES = ['delete_rate', 'add_markup']


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class HaulageFreightRateBulkOperation(BaseModel):
    action_name = CharField(index = True, null=True)
    created_at = DateTimeField(default=datetime.now())
    data = BinaryJSONField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    performed_by_id = UUIDField(null=True, index=True)
    performed_by = BinaryJSONField(null=True)
    sourced_by_id = UUIDField(null=True)
    sourced_by = BinaryJSONField(null=True)
    procured_by_id = UUIDField(null=True)
    procured_by = BinaryJSONField(null=True)
    progress = IntegerField(constraints=[SQL("DEFAULT 0")], index=True, null=True)
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)
    updated_at = DateTimeField(default=datetime.now())

    class Meta:
        table_name = 'haulage_freight_rate_bulk_operations'


    def validate_service_provider_id(self):
        if not self.service_provider_id:
            return

        service_provider_data = get_organization(id=self.service_provider_id)
        if len(service_provider_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid service provider ID")
        
    def validate_performed_by_id(self):
        data =  get_user(self.performed_by_id)
        if data:
            return True
        else:
            return False
        
    def validate_action_name(self):
        if self.action_name not in ACTION_NAMES:
            raise HTTPException(status_code=400,detail='Invalid action Name')
    
    def validate_delete_rate_data(self):
        return True
    
    def validate_add_markup_data(self):
        data = self.data

        if float(data['markup']) == 0:
            raise HTTPException(status_code=400, detail='markup cannot be 0')
        
        markup_types = ['net', 'percent']

        if data['markup_type'] not in markup_types:
            raise HTTPException(status_code=400, detail='markup_type is invalid')
        
        haulage_freight_charges_dict = HAULAGE_FREIGHT_CHARGES

        charge_codes = haulage_freight_charges_dict.keys()

        if data['line_item_code'] not in charge_codes:
            raise HTTPException(status_code=400, detail='line_item_code is invalid')
        
        if str(data['markup_type']).lower() == 'percent':
            return
        
    def perform_delete_rate_action(self,sourced_by_id,procured_by_id):
        data = self.data

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id})
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        haulage_freight_rates = list_haulage_freight_rates(filters = filters, return_query = True, page_limit = page_limit, pagination_data_required = False)['list']
        haulage_freight_rates = list(haulage_freight_rates.dicts())

        total_count = len(haulage_freight_rates)
        count = 0

        for freight in haulage_freight_rates:
            count = count + 1

            if HaulageFreightRateAudit.get_or_none(bulk_operation_id=self.id,object_id=freight["id"]):
                self.progress = int((count * 100.0) / total_count)
                self.save()
                continue

            delete_haulage_freight_rate({
                'id': str(freight["id"]),
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id,
                'sourced_by_id': sourced_by_id,
                'procured_by_id': procured_by_id,
            })

            self.progress = int((count * 100.0) / total_count)
            self.save()

    
    def perform_add_markup_action(self, sourced_by_id, procured_by_id):
        data = self.data

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id})
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        haulage_freight_rates = list_haulage_freight_rates(filters = filters, return_query = True, page_limit = page_limit, pagination_data_required = False)['list']
        haulage_freight_rates = list(haulage_freight_rates.dicts())

        total_count = len(haulage_freight_rates)
        count = 0

        for freight in haulage_freight_rates:
            count = count + 1

            if HaulageFreightRateAudit.get_or_none(bulk_operation_id=self.id):
                self.progress = int((count * 100.0) / total_count)
                self.save()
                continue

            line_items = [t for t in freight['line_items'] if t['code'] == data['line_item_code']]

            if not line_items:
                self.progress = int((count * 100.0) / total_count)
                self.save()

            freight['line_items'] = freight['line_items'] - line_items

            for line_item in line_items:
                if data['markup_type'].lower() == 'percent':
                    markup = float(data['markup'] * line_item['price']) / 100 
                else:
                    markup = data['markup']
                
                if data['markup_type'].lower() == 'net':
                    markup = common.get_money_exchange_for_fcl({'from_currency': data['markup_currency'], 'to_currency': line_item['currency'], 'price': markup})['price']

                line_item['price'] = line_item['price'] + markup

                if line_item['price'] < 0:
                    line_item['price'] = 0 

                for slab in line_item['slabs']:
                    if data['markup_type'].lower() == 'percent':
                        markup = float(data['markup'] * slab['price']) / 100 
                    else:
                        markup = data['markup']
                    
                    if data['markup_type'].lower() == 'net':
                        markup = common.get_money_exchange_for_fcl({'from_currency': data['markup_currency'], 'to_currency': line_item['currency'], 'price': markup})['price']

                    slab['price'] = slab['price'] + markup
                    if slab['price'] < 0:
                        slab['price'] = 0 

                freight['line_items'].append(line_item)

            
            update_haulage_freight_rate({
                    'id': freight['id'],
                    'performed_by_id': self.performed_by_id,
                    'sourced_by_id': sourced_by_id,
                    'procured_by_id': procured_by_id,
                    'bulk_operation_id': self.id,
                    'line_items': freight['data']
                })
            
            self.progress = int((count * 100.0) / total_count)
            self.save()

    
    def delete_rate_detail(self):
        return self
    
    def add_markup_detail(self):
        return self


    # def validate_action_data(self):

    #     if self.action_name == 'delete_rate':
    #         validate_delete_rate_data()
    #     if self.action_name == 'add_markup':
    #         validate_add_markup_data()