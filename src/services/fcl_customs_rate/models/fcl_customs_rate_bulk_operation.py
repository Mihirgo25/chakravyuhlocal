from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from database.rails_db import *
from fastapi import HTTPException
from configs.global_constants import FREE_DAYS_TYPES, ALL_COMMODITIES, CONTAINER_SIZES, CONTAINER_TYPES, MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from micro_services.client import common
from configs.definitions import FCL_CUSTOMS_CHARGES
from services.fcl_customs_rate.interactions.list_fcl_customs_rates import list_fcl_customs_rates
from services.fcl_customs_rate.models.fcl_customs_rate_audit import FclCustomsRateAudit
from services.fcl_customs_rate.interactions.delete_fcl_customs_rate import delete_fcl_customs_rate
from services.fcl_customs_rate.interactions.update_fcl_customs_rate import update_fcl_customs_rate

ACTION_NAMES = ['delete_rate', 'add_markup']

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclCustomsRateBulkOperation(BaseModel):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    progress = IntegerField(constraints=[SQL("DEFAULT 0")], index=True, null=True)
    action_name = CharField(index = True, null=True)
    performed_by_id = UUIDField(null=True, index=True)
    created_at = DateTimeField(default=datetime.now())
    data = BinaryJSONField(null=True)
    updated_at = DateTimeField(default=datetime.now())
    service_provider_id = UUIDField(index=True, null=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCustomsRateBulkOperation, self).save(*args, **kwargs)

    class Meta:
        table_name = 'fcl_customs_rate_bulk_operations'

    def validate_performed_by_id(self):
        data =  get_user(self.performed_by_id)
        if data:
            return True
        else:
            return False
        
    def validate_service_provider_id(self):
        if not self.service_provider_id:
            return

        service_provider_data = get_organization(id=self.service_provider_id)
        if len(service_provider_data) == 0:
            raise HTTPException(status_code=400, detail="Invalid service provider ID")
        
    def validate_action_name(self):
        if self.action_name not in ACTION_NAMES:
            raise HTTPException(status_code=400,detail='Invalid action Name')
        
    def validate_delete_rate_data(self):
        return
    
    def validate_add_markup_data(self):
        data = self.data
        markup_types = ['net', 'percent']

        if data['markup_type'] not in markup_types:
            raise HTTPException(status_code=400,detail='Invalid Markup Type')
        
        fcl_customs_charges_dict = FCL_CUSTOMS_CHARGES

        charge_codes = fcl_customs_charges_dict.keys()

        if data['line_item_code'] not in charge_codes:
            raise HTTPException(status_code=400, detail='line_item_code is invalid')
        
        if str(data['markup_type']).lower() == 'percent':
            return
        
        # currencies = FCL_CUSTOMS_CURRENCIES['list']

        # if data['markup_currency'] not in currencies:
        #     raise HTTPException(status_code=400, detail='markup currency is invalid')

    def perform_delete_rate_action(self, sourced_by_id, procured_by_id):
        data = self.data

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id})
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_customs_rates = list_fcl_customs_rates(filters = filters, return_query = True, page_limit = page_limit)['list']
        fcl_customs_rates = list(fcl_customs_rates.dicts())

        total_count = len(fcl_customs_rates)
        count = 0

        for customs in fcl_customs_rates:
            count += 1

            if FclCustomsRateAudit.get_or_none(bulk_operation_id = self.id, object_id = customs['id']):
                self.progress = int((count * 100.0) / total_count)
                self.save()
                continue

            delete_fcl_customs_rate({
                'id': customs['id'],
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id,
                'procured_by_id': procured_by_id,
                'sourced_by_id': sourced_by_id
            })

            self.progress = int((count * 100.0) / total_count)
            self.save()

    def perform_add_markup_action(self, sourced_by_id, procured_by_id):
        data = self.data

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id})
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_customs_rates = list_fcl_customs_rates(filters = filters, return_query = True, page_limit = page_limit)['list']
        fcl_customs_rates = list(fcl_customs_rates.dicts())

        total_count = len(fcl_customs_rates)
        count = 0

        for customs in fcl_customs_rates:
            count += 1

            if FclCustomsRateAudit.get_or_none(bulk_operation_id = self.id, object_id = customs['id']):
                self.progress = int((count * 100.0) / total_count)
                self.save()
                continue

            line_items = [t for t in customs['customs_line_items'] if t['code'] == data['line_item_code']]

            if not line_items:
                self.progress = int((count * 100.0) / total_count)
                self.save()
                continue

            customs['customs_line_items'] = [t for t in customs['customs_line_items'] if t not in line_items]

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

                customs['customs_line_items'].append(line_item)

            update_fcl_customs_rate({
                'id': customs['id'],
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id,
                'customs_line_items': customs['customs_line_items'],
                'cfs_line_items': customs['cfs_line_items'],
                'procured_by_id': procured_by_id,
                'sourced_by_id': sourced_by_id
            })

            self.progress = int((count * 100.0) / total_count)
            self.save()

    def delete_rate_detail():
        return
    
    def add_markup_detail():
        return