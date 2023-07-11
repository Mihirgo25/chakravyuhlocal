from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from datetime import datetime
from database.rails_db import *
from fastapi import HTTPException
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from micro_services.client import common
from configs.definitions import AIR_CUSTOMS_CHARGES, FCL_FREIGHT_CURRENCIES

from services.air_customs_rate.interaction.list_air_customs_rates import list_air_customs_rates
from services.air_customs_rate.models.air_customs_rate_audit import AirCustomsRateAudit
from services.air_customs_rate.interaction.delete_air_customs_rate import delete_air_customs_rate
from services.air_customs_rate.interaction.update_air_customs_rate import update_air_customs_rate
from services.air_customs_rate.models.air_customs_rate import AirCustomsRate

ACTION_NAMES = ['delete_rate', 'add_markup']

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class AirCustomsRateBulkOperation(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    progress = IntegerField(constraints=[SQL("DEFAULT 0")], null=True)
    action_name = CharField(index = True, null=True)
    performed_by_id = UUIDField(index=True, null=True)
    created_at = DateTimeField(default=datetime.now())
    data = BinaryJSONField(null=True)
    updated_at = DateTimeField(default=datetime.now())
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(AirCustomsRateBulkOperation, self).save(*args, **kwargs)

    class Meta:
        table_name = 'air_customs_rate_bulk_operations'

    def processed_percent_key(self, id):
        return f"air_customs_rate_bulk_operation_{id}"

    def set_processed_percent_air_customs_bulk_operation(self, processed_percent, id):
        processed_percent_hash = "process_percent_air_customs_bulk_operation"
        if rd:
            rd.hset(processed_percent_hash, self.processed_percent_key(id), processed_percent) 

    def validate_delete_rate_data(self):
        return
    
    def validate_add_markup_data(self):
        data = self.data

        if data.get('markup') == 0:
            raise HTTPException(status_code=400, detail='Markup cannot be 0')
        
        markup_types = ['net', 'percent']

        if data.get('markup_type') not in markup_types:
            raise HTTPException(status_code=400, detail='Markup is invalid')

        charge_codes = AIR_CUSTOMS_CHARGES.keys()

        if data.get('line_item_code') not in charge_codes:
            raise HTTPException(status_code=400, detail='Line Item Code is invalid')

        if data.get('markup_type').lower() == 'percent':
            return
        
        currencies = FCL_FREIGHT_CURRENCIES

        if data['markup_currency'] not in currencies:
            raise HTTPException(status_code=400, detail='markup currency is invalid')
    
    def perform_delete_rate_action(self):
        data = self.data
        count = 0

        total_count = len(data)
        for custom_data in data:
            count += 1
            object = AirCustomsRate.select().where(
                AirCustomsRate.id == custom_data.get('air_customs_rate_id'))

            try:
                object = object.get()
            except:
                raise HTTPException(status_code=400, detail='Rate is not present')

            if AirCustomsRateAudit.get_or_none(bulk_operation_id = self.id, object_id = custom_data.get('id')):
                self.progress = int((count * 100.0) / total_count)
                self.set_processed_percent_air_customs_bulk_operation(self.progress, self.id)
                continue

            delete_air_customs_rate({
                'id': custom_data.get('air_customs_rate_id'),
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id
            })

            self.progress = int((count * 100.0) / total_count)
            self.set_processed_percent_air_customs_bulk_operation(self.progress, self.id)
        self.save()

    def perform_add_markup_action(self, sourced_by_id, procured_by_id):
        data = self.data
        filters = (data.get('filters') or {}) | {'service_provider_id': self.service_provider_id, 'importer_exporter_present': False }
        
        air_customs_rates = list_air_customs_rates(
            filters = filters, 
            return_query = True, 
            page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
            )['list']
        
        total_count = len(air_customs_rates.dicts())
        count = 0

        for customs in air_customs_rates:
            count += 1

            if AirCustomsRateAudit.get_or_none(bulk_operation_id = self.id, object_id = customs['id']):
                self.progress = int((count * 100.0) / total_count)
                self.set_processed_percent_air_customs_bulk_operation(self.progress, self.id)
                continue
            
            line_items = [t for t in customs['line_items'] if t['code'] == data['line_item_code']]

            if not line_items:
                self.progress = int((count * 100.0) / total_count)
                self.set_processed_percent_air_customs_bulk_operation(self.progress, self.id)
                continue

            customs['line_items'] = [t for t in customs['line_items'] if t not in line_items]

            for line_item in line_items:
                if data['markup_type'].lower() == 'percent':
                    markup = (data['markup'] * line_item['price']) / 100
                else:
                    markup = data['markup']

                if data['markup_type'].lower() == 'net':
                    markup = common.get_money_exchange_for_fcl({'from_currency': data['markup_currency'], 'to_currency': line_item['currency'], 'price': markup})['price']

                line_item['price'] = line_item['price'] + markup
                if line_item['price'] < 0:
                    line_item['price'] = 0 

                customs['line_items'].append(line_item)

            update_air_customs_rate({
                'id': customs['id'],
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id,
                'procured_by_id': procured_by_id,
                'sourced_by_id': sourced_by_id,
                'line_items': customs['line_items']
            })

            self.progress = int((count * 100.0) / total_count)
            self.set_processed_percent_air_customs_bulk_operation(self.progress, self.id)
        self.save()