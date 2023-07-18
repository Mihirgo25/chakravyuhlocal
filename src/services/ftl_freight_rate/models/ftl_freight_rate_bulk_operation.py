
from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from fastapi import HTTPException
from services.ftl_freight_rate.interactions.list_ftl_freight_rates import list_ftl_freight_rates
from services.ftl_freight_rate.models.ftl_freight_rate_audit import FtlFreightRateAudit
from services.ftl_freight_rate.models.ftl_freight_rate import FtlFreightRate
from services.ftl_freight_rate.interactions.update_ftl_freight_rate import update_ftl_freight_rate
from services.ftl_freight_rate.interactions.delete_ftl_freight_rate import delete_ftl_freight_rate
from configs.definitions import FTL_FREIGHT_CHARGES
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from configs.ftl_freight_rate_constants import DEFAULT_RATE_TYPE
from libs.parse_numeric import parse_numeric
from configs.definitions import FTL_FREIGHT_CURRENCIES
import json
from micro_services.client import *
from database.rails_db import *

ACTION_NAMES = ['delete_rate', 'add_markup']
MARKUP_TYPES = ['net', 'percent']


class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FtlFreightRateBulkOperation(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    action_name = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now, index=True)
    data = BinaryJSONField(null=True)
    performed_by_id = UUIDField(index=True, null =True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    service_provider_id = UUIDField(null=True)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FtlFreightRateBulkOperation, self).save(*args, **kwargs)
    
    class Meta:
        table_name = 'ftl_freight_rate_bulk_operations'

    progress_percent_hash = "bulk_operation_progress"

    def progress_percent_key(self):
        return f"bulk_operations_{self.id}"
    
    def get_progress_percent(id, progress = 0):
        progress_percent_hash = "bulk_operation_progress"
        progress_percent_key =  f"bulk_operations_{id}"
        
        if rd:
            try:
                cached_response = rd.hget(progress_percent_hash, progress_percent_key)
                return max(parse_numeric(cached_response) or 0, progress)
            except:
                return progress
        else: 
            return progress

    def set_progress_percent(self,progress_percent):
        if rd:
            rd.hset(self.progress_percent_hash, self.progress_percent_key(), progress_percent)

    def validate_action_name(self):
        if self.action_name not in ACTION_NAMES:
            raise HTTPException(status_code=400,detail='Invalid action Name')

    def validate_delete_rate_data(self):
        return True

    def validate_add_markup_data(self):
        data = self.data

        if data['markup_type'] not in MARKUP_TYPES:
            raise HTTPException(status_code=400, detail='is invalid')

        ftl_freight_charges_dict = FTL_FREIGHT_CHARGES

        charges_code = ftl_freight_charges_dict.keys()
        
        if data['line_item_code'] not in charges_code:
            raise HTTPException(status_code=400, detail='is invalid')
        
        currencies = FTL_FREIGHT_CURRENCIES

        if data['markup_currency'] not in currencies:
            raise HTTPException(status_code=400, detail='is invalid')

    def perform_delete_rate_action(self, sourced_by_id, procured_by_id):
        data = self.data
        total_affected_rates = 0

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id})

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        ftl_freight_rate = list_ftl_freight_rates(filters= filters, return_query= True, page_limit= page_limit)['list']

        total_count = len(ftl_freight_rate)
        count = 0

        for freight in ftl_freight_rate:
            count+=1

            if FtlFreightRateAudit.get_or_none(bulk_operation_id = self.id, object_id = freight["id"]):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            delete_ftl_freight_rate({
                'id': str(freight["id"]),
                'sourced_by_id': sourced_by_id,
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id,
                'procured_by_id': procured_by_id
            })
            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_progress_percent(progress)

        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else self.get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()
    
    def perform_add_markup_action(self, sourced_by_id, procured_by_id):
        data = self.data
        total_affected_rates = 0
        
        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id })

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        ftl_freight_rates = list_ftl_freight_rates(filters= filter, return_query=True, page_limit= page_limit)['List']

        total_count = len(ftl_freight_rates)
        count = 0

        for freight in ftl_freight_rates:
            count+=1

            if FtlFreightRateAudit.get_or_none(bulk_operation_id = self.id, object_id = freight['id']):
                progress = int((count * 100.0)) / total_count
                self.set_progress_percent(progress)
                continue

            freight = freight.as_json
            
            line_items = [t for t in freight['line_items'] if t['code'] == data['line_item_code']]

            if line_items:
                progress = int((count * 100.0)) / total_count
                self.set_progress_percent(progress)
                continue

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

                freight['line_items'].append(line_item)

                update_ftl_freight_rate({
                    'id': freight['id'],
                    'performed_by_id': self.performed_by_id,
                    'sourced_by_id': sourced_by_id,
                    'procured_by_id': procured_by_id,
                    'bulk_operation_id': self.id,
                    'data': freight['data']
                })

            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_progress_percent(progress)

        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else self.get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()


    def delete_rate_details(self):
        return  json.dumps(self)
    
    def add_markup_details(self):
        return  json.dumps(self)