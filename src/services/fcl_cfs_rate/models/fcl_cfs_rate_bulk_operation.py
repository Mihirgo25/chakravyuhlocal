from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
from micro_services.client import *
from database.rails_db import *
import datetime
from fastapi import HTTPException
from services.fcl_cfs_rate.interaction.list_fcl_cfs_rate import list_fcl_cfs_rate
from services.fcl_cfs_rate.interaction.delete_fcl_cfs_rate import delete_fcl_cfs_rate
from services.fcl_cfs_rate.models.fcl_cfs_rate_audit import FclCfsRateAudit
from configs.global_constants import MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from configs.definitions import FCL_CFS_CHARGES,FCL_FREIGHT_CURRENCIES
from services.fcl_cfs_rate.interaction.update_fcl_cfs_rate import update_fcl_cfs_rate
ACTION_NAMES = ['delete_rate']


class FclCfsRateBulkOperation(Model):
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True, index=True)
    service_provider_id = CharField(null = True)
    performed_by_id = CharField(null = True)
    data = BinaryJSONField(null=True)
    progress = IntegerField(null=True)
    action_name = CharField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super(FclCfsRateBulkOperation, self).save(*args, **kwargs)

    class Meta:
        database = db
        table_name = 'fcl_cfs_rate_bulk_operations'
        
    def perform_delete_rate_action(self, sourced_by_id, procured_by_id):
        data = self.data
        
        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False})
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
        fcl_cfs_rates = list_fcl_cfs_rate(filters = filters, return_query = True, page_limit = page_limit)['list']
        fcl_cfs_rates = list(fcl_cfs_rates.dicts())

        total_count = len(fcl_cfs_rates)
        count = 0

        for freight in fcl_cfs_rates:
            count += 1

            if FclCfsRateAudit.get_or_none(bulk_operation_id=self.id,object_id=freight["id"]):
                self.progress = int((count * 100.0) / total_count)
                self.save()
                continue

            delete_fcl_cfs_rate({
                'id': str(freight.get("id")),
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id,
                'sourced_by_id': sourced_by_id,
                'procured_by_id': procured_by_id,
            })

            self.progress = int((count * 100.0) / total_count)
            self.save()

    def validate_delete_rate_data(self):
        pass

    def validate_add_markup_data(self):
        data = self.data
        markup_types = ['net', 'percent']
        if data['markup_type'] not in markup_types:
            raise HTTPException(status_code=400,detail='Invalid Markup Type')
        
        fcl_cfs_charges_dict = FCL_CFS_CHARGES

        charge_codes = fcl_cfs_charges_dict.keys()

        if data['line_item_code'] not in charge_codes:
            raise HTTPException(status_code=400, detail='line_item_code is invalid')
        
        if str(data['markup_type']).lower() == 'percent':
            return
        
        currencies = FCL_FREIGHT_CURRENCIES

        if data['markup_currency'] not in currencies:
            raise HTTPException(status_code=400, detail='markup currency is invalid')
        
    def perform_add_markup_action(self, sourced_by_id, procured_by_id):
        data = self.data
        
        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id})
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_cfs_rates = list_fcl_cfs_rate(filters = filters, return_query = True, page_limit = page_limit)['list']
        fcl_cfs_rates = list(fcl_cfs_rates.dicts())

        total_count = len(fcl_cfs_rates)
        count = 0
        
        for cfs in fcl_cfs_rates:
            count += 1
            
            if FclCfsRateAudit.get_or_none(bulk_operation_id = self.id, object_id = cfs['id']):
                self.progress = int((count * 100.0) / total_count)
                self.save()
                continue

            line_items = [t for t in cfs['line_items'] if t['code'] == data['line_item_code']]

            if not line_items:
                self.progress = int((count * 100.0) / total_count)
                self.save()
                continue
            
            cfs['line_items'] = [t for t in cfs['line_items'] if t not in line_items]

            for line_item in line_items:
                if data['markup_type'].lower() == 'percent':
                    markup = float(data['markup'] * line_item['price']) / 100 
                else:
                    markup = data['markup']

                if data['markup_type'].lower() == 'net':
                    markup = common.get_money_exchange_for_fcl({'from_currency': data.get('markup_currency'), 'to_currency': line_item.get('currency'), 'price': markup})['price']

                line_item['price'] = line_item['price'] + markup

                if line_item['price'] < 0:
                    line_item['price'] = 0 

                cfs['line_items'].append(line_item)

            update_fcl_cfs_rate({
                'id': cfs.get('id'),
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id,
                'line_items': cfs['line_items'],
                'procured_by_id': procured_by_id,
                'sourced_by_id': sourced_by_id
            })

            self.progress = int((count * 100.0) / total_count)
            self.save()