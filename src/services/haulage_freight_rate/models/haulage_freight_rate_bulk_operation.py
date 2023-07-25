from database.db_session import db
from peewee import * 
from playhouse.postgres_ext import BinaryJSONField, DateTimeTZField
from micro_services.client import *
from fastapi import HTTPException
from datetime import datetime
from database.rails_db import *
from configs.definitions import HAULAGE_FREIGHT_CHARGES, FCL_FREIGHT_CURRENCIES
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.haulage_freight_rate.models.haulage_freight_rate_audit import HaulageFreightRateAudit
from services.haulage_freight_rate.interactions.list_haulage_freight_rates import list_haulage_freight_rates
from services.haulage_freight_rate.interactions.delete_haulage_freight_rate import delete_haulage_freight_rate
from services.haulage_freight_rate.interactions.update_haulage_freight_rate import update_haulage_freight_rate
from services.haulage_freight_rate.helpers.haulage_freight_rate_helpers import get_progress_percent, processed_percent_key, set_progress_percent, set_total_affected_rates
from libs.parse_numeric import parse_numeric
from fastapi.encoders import jsonable_encoder


ACTION_NAMES = ['delete_rate', 'add_markup']
BATCH_SIZE = 1000

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class HaulageFreightRateBulkOperation(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    action_name = TextField(index = True, null=True)
    progress = IntegerField(constraints=[SQL("DEFAULT 0")], index=True, null=True)
    data = BinaryJSONField(null=True)
    performed_by_id = UUIDField(null=True, index=True)
    service_provider_id = UUIDField(index=True, null=True)
    updated_at = DateTimeField(default=datetime.now())
    created_at = DateTimeField(default=datetime.now())

    class Meta:
        table_name = 'haulage_freight_rate_bulk_operations'
        
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

        if data.get('markup_type') not in markup_types:
            raise HTTPException(status_code=400, detail='markup_type is invalid')
        
        haulage_freight_charges_dict = HAULAGE_FREIGHT_CHARGES

        charge_codes = haulage_freight_charges_dict.keys()

        if data.get('line_item_code') not in charge_codes:
            raise HTTPException(status_code=400, detail='line_item_code is invalid')
        
        if str(data['markup_type']).lower() == 'percent':
            return
        
        currencies = FCL_FREIGHT_CURRENCIES

        if data.get('markup_currency') not in currencies:
            raise HTTPException(status_code=400, detail='markup_currency is invalid')
        
    def perform_delete_rate_action(self, sourced_by_id, procured_by_id):
        data = self.data
        total_affected_rates = 0

        filters = (data['filters'] or {})
        filters["service_provider_id"] = self.service_provider_id
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        includes = {'id': True}

        query = list_haulage_freight_rates(filters = filters, page_limit = page_limit, pagination_data_required = False, return_query = True, includes=includes)['list']
        total_count =  query.count()
        count = 0
        offset = 0

        while offset < total_count:
            batch_query = query.offset(offset).limit(BATCH_SIZE)
            offset += BATCH_SIZE
            count, total_affected_rates = self.perform_batch_delete_freight_rate_action(batch_query,  count , total_count, total_affected_rates, sourced_by_id, procured_by_id)

        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else  get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()  
    
    def perform_batch_delete_freight_rate_action(self, batch_query,  count , total_count, total_affected_rates, sourced_by_id, procured_by_id):
        haulage_freight_rates = list(batch_query.dicts())
        for freight in haulage_freight_rates:
            count += 1
            if HaulageFreightRateAudit.get_or_none(bulk_operation_id=self.id,object_id=freight["id"]):
                progress = int((count * 100.0) / total_count)
                set_progress_percent(progress)
                continue

            delete_haulage_freight_rate({
                'id': str(freight["id"]),
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id,
                'sourced_by_id': sourced_by_id,
                'procured_by_id': procured_by_id,
            })
            progress = int((count * 100.0) / total_count)
            total_affected_rates += 1
            set_total_affected_rates(total_affected_rates, self.id)
            set_progress_percent(progress, self.id)
        return count, total_affected_rates


    
    def perform_add_markup_action(self, sourced_by_id, procured_by_id):
        total_affected_rates = 0
        data = self.data

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id})
        includes = { 
                    'id': True,
                    'performed_by_id': True,
                    'origin_location_id': True,
                    'destination_location_id': True,
                    'container_size': True,
                    'container_type': True,
                    'commodity': True,
                    'shipping_line_id': True,
                    'importer_exporter_id': True,
                    'service_provider_id': True,
                    'sourced_by_id': True,
                    'procured_by_id': True,

                }

        query = list_haulage_freight_rates(filters = filters, page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT, pagination_data_required = False, includes = includes, return_query= True)['list']
        total_count = query.count()

        count = 0
        offset = 0

        while offset < total_count:
            batch_query = query.offset(offset).limit(BATCH_SIZE)
            offset += BATCH_SIZE
            count, total_affected_rates = self.perform_batch_add_freight_rate_markup_action(batch_query, count , total_count, total_affected_rates, sourced_by_id, procured_by_id)
        
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else  get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()



    def perform_batch_add_freight_rate_markup_action(self, batch_query, count , total_count, total_affected_rates, sourced_by_id, procured_by_id):
        data = self.data
        haulage_freight_rates = list(batch_query.dicts())

        for freight in haulage_freight_rates:
            count += 1
            if HaulageFreightRateAudit.get_or_none(bulk_operation_id=self.id,object_id=freight["id"]):
                progress = int((count * 100.0) / total_count)
                set_progress_percent(progress, self.id)
                continue
            line_items = [t for t in freight['line_items'] if t['code'] == data['line_item_code']]
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

                if line_item['slabs']:
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
                        'id': str(freight['id']),
                        'performed_by_id': self.performed_by_id,
                        'sourced_by_id': sourced_by_id,
                        'procured_by_id': procured_by_id,
                        'bulk_operation_id': self.id,
                        'line_items': freight['line_items']
                    })
            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            set_total_affected_rates(total_affected_rates, self.id)
            set_progress_percent(progress, self.id)

        return count, total_affected_rates

    
    def delete_rate_detail(self):
        return self
    
    def add_markup_detail(self):
        return self
