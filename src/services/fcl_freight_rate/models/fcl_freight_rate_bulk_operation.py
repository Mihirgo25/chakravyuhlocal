from database.db_session import db
from peewee import * 
from playhouse.postgres_ext import *
from rails_client import client
from fastapi import HTTPException
from datetime import datetime
from configs.defintions import FCL_FREIGHT_CHARGES
import yaml
from configs.global_constants import FREE_DAYS_TYPES, ALL_COMMODITIES, CONTAINER_SIZES, CONTAINER_TYPES, MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate import delete_fcl_freight_rate
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_local import update_fcl_freight_rate_local
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_free_day import update_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.update_fcl_freight_rate import update_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import list_fcl_freight_rates
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_locals import list_fcl_freight_rate_locals
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_free_days import list_fcl_freight_rate_free_days
from services.fcl_freight_rate.models.fcl_freight_rate_audits import FclFreightRateAudit

ACTION_NAMES = ['extend_validity', 'delete_freight_rate', 'add_freight_rate_markup', 'add_local_rate_markup', 'update_free_days_limit', 'add_freight_line_item', 'update_free_days', 'update_weight_limit', 'extend_freight_rate', 'extend_freight_rate_to_icds', 'delete_local_rate']


class BaseModel(Model):
    class Meta:
        database = db

class FclFreightRateBulkOperation(BaseModel):
    action_name = CharField(null=True)
    created_at = DateTimeField()
    data = BinaryJSONField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    performed_by_id = UUIDField(null=True)
    progress = IntegerField(constraints=[SQL("DEFAULT 0")], index=True, null=True)
    service_provider_id = UUIDField(null=True)
    updated_at = DateTimeField()

    class Meta:
        table_name = 'fcl_freight_rate_bulk_operations'

    def validate_service_provider(self):
        if not self.service_provider_id:
            return True
        service_provider_data = client.ruby.list_organizations({'filters':{'id': str(self.service_provider_id)}})
        if service_provider_data.get('account_type') == 'service_provider':
            return True
        return False
    
    def validate_performed_by_id(self):
        if not self.service_provider_id:
            return True
        performed_by_data = client.ruby.list_users({'filters':{'id': str(self.performed_by_id)}})
        if performed_by_data:
            return True
        return False
    
    def validate_action_name(self):
        if self.action_name in ACTION_NAMES:
            return True
        return False
    
    def validity_extend_validity_data(self):
        data = self.data

        if datetime.strptime(data['validity_end'], '%Y-%m-%d') < datetime.strptime(data['source_date'], '%Y-%m-%d'):
            raise HTTPException(status_code=499, detail='validity_end cannot be less than source date')
        
        if datetime.strptime(data['validity_end'], '%Y-%m-%d') < datetime.date.today():
            raise HTTPException(status_code=499, detail='validity_end cannot be less than current date')
        
        if datetime.strptime(data['validity_end'], '%Y-%m-%d') > (datetime.date.today() + datetime.timedelta(days=60)):
            raise HTTPException(status_code=499, detail='validity_end cannot be greater than 60 days')

    def validate_delete_freight_rate_data(self):
        data = self.data

        if datetime.strptime(data['validity_end'], '%Y-%m-%d') < datetime.strptime(data['validity_start'], '%Y-%m-%d'):
            raise HTTPException(status_code=499, detail='validity_end cannot be less than validity start')
        
    def validate_delete_local_rate_data(self):
        return True
    
    def validate_add_freight_rate_markup_data(self):
        data = self.data

        if float(data['markup']) == 0:
            raise HTTPException(status_code=499, detail='markup cannot be 0')
    
        markup_types = ['net', 'percent']

        if data['markup_type'] not in markup_types:
            raise HTTPException(status_code=499, detail='markup_type is invalid')
        
        if datetime.strptime(data['validity_end'], '%Y-%m-%d') < datetime.date.today():
            raise HTTPException(status_code=499, detail='validity_end cannot be less than current date')
        
        if datetime.strptime(data['validity_end'], '%Y-%m-%d') < datetime.strptime(data['validity_start'], '%Y-%m-%d'):
            raise HTTPException(status_code=499, detail='validity_end cannot be less than validity start')
        
        fcl_freight_charges_dict = FCL_FREIGHT_CHARGES

        charge_codes = fcl_freight_charges_dict.keys()

        if data['line_item_code'] not in charge_codes:
            raise HTTPException(status_code=499, detail='line_item_code is invalid')
        
        if str(data['markup_type']).lower() == 'percent':
            return
        
        currencies = [t['iso_code'] for t in client.ruby.list_money_currencies()['list']]

        if data['markup_currency'] not in currencies:
            raise HTTPException(status_code=499, detail='markup_currency is invalid')
        
    def validate_add_local_rate_markup_data(self):
        data = self.data

        if float(data['markup']) == 0:
            raise HTTPException(status_code=499, detail='markup cannot be 0')
        
        markup_types = ['net', 'percent']

        if data['markup_type'] not in markup_types:
            raise HTTPException(status_code=499, detail='markup_type is invalid')
        
        fcl_freight_charges_dict = FCL_FREIGHT_CHARGES

        charge_codes = fcl_freight_charges_dict.keys()

        if data['line_item_code'] not in charge_codes:
            raise HTTPException(status_code=499, detail='line_item_code is invalid')
        
        if str(data['markup_type']).lower() == 'percent':
            return
        
        currencies = [t['iso_code'] for t in client.ruby.list_money_currencies()['list']]

        if data['markup_currency'] not in currencies:
            raise HTTPException(status_code=499, detail='markup_currency is invalid')

    def validate_update_free_days_limit_data(self):
        data = self.data

        if int(data['free_limit']) <= 0:
            raise HTTPException(status_code=499, detail='free_limit cannot be less than or equal to 0')
        
        slabs = sorted(data.get('slabs', []), key=lambda slab: slab.get('lower_limit', 0))

        if any(slab.get('upper_limit', 0) <= slab.get('lower_limit', 0) for slab in slabs):
            raise HTTPException(status_code=499, detail='slabs is invalid')

        if slabs[0] and (int(slabs[0]['lower_limit']) <= int(data['free_limit'])):
            raise HTTPException(status_code=499, detail='slabs lower limit should be greater than free limit')\

        if any(index > 0 and slab.get('lower_limit', 0) <= slabs[index - 1].get('upper_limit', 0) for index, slab in enumerate(slabs)):
            raise HTTPException(status_code=499, detail='slabs is invalid')

        currencies = slabs['currency']
        valid_currencies = [t['iso_code'] for t in client.ruby.list_money_currencies()['list']]

        if currencies - valid_currencies:
            raise HTTPException(status_code=499, detail='slabs.currency is invalid')

    def validate_add_freight_line_item_data(self):
        data = self.data

        fcl_freight_charges_dict = FCL_FREIGHT_CHARGES

        code_config = fcl_freight_charges_dict[data['code']]

        if not code_config:
            raise HTTPException(status_code=499, detail='code is invalid')
        
        if data['units'] not in code_config['units']:
            raise HTTPException(status_code=499, detail='unit is invalid')
        
        valid_currencies = [t['iso_code'] for t in client.ruby.list_money_currencies()['list']]

        if data['currency'] not in valid_currencies:
            raise HTTPException(status_code=499, detail='currency is invalid')
        
        if datetime.strptime(data['validity_end'], '%Y-%m-%d') < datetime.date.today():
            raise HTTPException(status_code=499, detail='validity_end cannot be less than current date')
        
        if datetime.strptime(data['validity_end'], '%Y-%m-%d') < datetime.strptime(data['validity_start'], '%Y-%m-%d'):
            raise HTTPException(status_code=499, detail='validity_end cannot be less than validity start')
        
    def validate_update_free_days_data(self):
        data = self.data

        if data['free_days_type'] not in FREE_DAYS_TYPES:
            raise HTTPException(status_code=499, detail='free_days_type is invalid')
        
        if int(data['free_limit']) <= 0:
            raise HTTPException(status_code=499, detail='free_limit cannot be less than or equal to 0')
        
        slabs = sorted(data.get('slabs', []), key=lambda slab: slab.get('lower_limit', 0))

        if any(slab.get('upper_limit', 0) <= slab.get('lower_limit', 0) for slab in slabs):
            raise HTTPException(status_code=499, detail='slabs is invalid')

        if slabs[0] and (int(slabs[0]['lower_limit']) <= int(data['free_limit'])):
            raise HTTPException(status_code=499, detail='slabs lower limit should be greater than free limit')

        if any(index > 0 and slab.get('lower_limit', 0) <= slabs[index - 1].get('upper_limit', 0) for index, slab in enumerate(slabs)):
            raise HTTPException(status_code=499, detail='slabs is invalid')

    def validate_update_weight_limit_data(self):
        data = self.data

        if int(data['free_limit']) <= 0:
            raise HTTPException(status_code=499, detail='free_limit cannot be less than or equal to 0')
        
        slabs = sorted(data.get('slabs', []), key=lambda slab: slab.get('lower_limit', 0))

        if any(slab.get('upper_limit', 0) <= slab.get('lower_limit', 0) for slab in slabs):
            raise HTTPException(status_code=499, detail='slabs is invalid')

        if slabs[0] and (int(slabs[0]['lower_limit']) <= int(data['free_limit'])):
            raise HTTPException(status_code=499, detail='slabs lower limit should be greater than free limit')\

        if any(index > 0 and slab.get('lower_limit', 0) <= slabs[index - 1].get('upper_limit', 0) for index, slab in enumerate(slabs)):
            raise HTTPException(status_code=499, detail='slabs is invalid')

    def validate_extend_freight_rate_data(self):
        data = self.data

        if data['commodities'] - ALL_COMMODITIES != None:
            raise HTTPException(status_code=499, detail='commodities is invalid')
        
        if data['container_sizes'] - CONTAINER_SIZES != None:
            raise HTTPException(status_code=499, detail='container_sizes is invalid')
        
        if data['container_types'] - CONTAINER_TYPES != None:
            raise HTTPException(status_code=499, detail='container_types is invalid')
        
        markup_types = ['net', 'percent']

        if data['markup_type'] not in markup_types:
            raise HTTPException(status_code=499, detail='markup_type is invalid')
        
        valid_currencies = [t['iso_code'] for t in client.ruby.list_money_currencies()['list']]

        if data['currency'] not in valid_currencies:
            raise HTTPException(status_code=499, detail='currency is invalid')
        
    def validate_extend_freight_rate_to_icds_data(self):
        data = self.data

        markup_types = ['net', 'percent']

        if data['markup_type'] not in markup_types:
            raise HTTPException(status_code=499, detail='markup_type is invalid')
        
        valid_currencies = [t['iso_code'] for t in client.ruby.list_money_currencies()['list']]
        
        if data['currency'] not in valid_currencies:
            raise HTTPException(status_code=499, detail='currency is invalid')
        
        if self.data['origin_port_ids'] or self.data['destination_port_ids']:
            rate_id = data['filters']['id']
            if not rate_id:
                raise HTTPException(status_code=499, detail='rate_id is not present')
            
            if not isinstance(rate_id, str):
                rate_id = rate_id[0]

            rate = FclFreightRate.find_by_id(rate_id)
            locations = client.ruby.list_locations({'filters': { 'id': [rate.origin_port_id, rate.destination_port_id] }, 'includes': { 'icd_ports': {} }})['list']
            origin_icd_location = [t for t in locations if t['id'] == rate.origin_port_id][0]['icd_ports']['id']
            
            destination_icd_location = [t for t in locations if t['id']== rate.destination_port_id][0]['icd_ports']['id']
            [t for t in locations if t['id']== rate.destination_port_id][0]['icd_ports']['id']
            if self.data['origin_port_ids'] - origin_icd_location != None:
                raise HTTPException(status_code=499, detail='origin_icd_port_id is invalid')
            
            if self.data['destination_port_ids'] - destination_icd_location != None:
                raise HTTPException(status_code=499, detail='destination_icd_port_id is invalid')
            
    def perform_extend_validity_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
        data = self.data
        sourced_by_ids = data['sourced_by_ids']
        procured_by_ids = data['procured_by_ids']

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_freight_rates = list_fcl_freight_rates(filters = filters, return_query = True, page_limit = page_limit)['list']

        total_count = fcl_freight_rates.__sizeof__
        count = 0

        for freight in fcl_freight_rates:
            count += 1
            try:
                actual_sourced_by_id = sourced_by_ids[freight.id]
            except:
                actual_sourced_by_id = None
            
            try:
                actual_procured_by_id = procured_by_ids[freight.id]
            except:
                actual_procured_by_id = None

            validity_object = None
            for t in freight.validities:
                if t.validity_start <= data['source_date'] and t.validity_end >= data['source_date'] and t.validity_end < data['validity_end']:
                    validity_object = t

            if not validity_object:
                self.progress = int((count * 100.0) / total_count)

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                self.progress = int((count * 100.0) / total_count)
                continue

            validity_start = max(datetime.strptime(validity_object.validity_start, '%Y-%m-%d'), datetime.date.today())
            validity_end = min(datetime.strptime(data['validity_end'], '%Y-%m-%d'), (datetime.date.today() + datetime.timedelta(days=60)))

            if actual_sourced_by_id:
                sourced_by_id_data = actual_sourced_by_id 
            else:
                sourced_by_id_data = sourced_by_id 

            if actual_procured_by_id:
                procured_by_id_data = actual_procured_by_id
            else:
                procured_by_id_data = procured_by_id

            create_fcl_freight_rate_data({
                'origin_port_id': freight.origin_port_id,
                'origin_main_port_id': freight.origin_main_port_id,
                'destination_port_id': freight.destination_port_id,
                'destination_main_port_id': freight.destination_main_port_id,
                'container_size': freight.container_size,
                'container_type': freight.container_type,
                'commodity': freight.commodity,
                'shipping_line_id': freight.shipping_line_id,
                'importer_exporter_id': freight.importer_exporter_id,
                'service_provider_id': freight.service_provider_id,
                'cogo_entity_id': freight.cogo_entity_id,
                'bulk_operation_id': self.id,
                'performed_by_id': self.performed_by_id,
                'sourced_by_id': sourced_by_id_data,
                'procured_by_id': procured_by_id_data,
                'validity_start': validity_start,
                'validity_end': validity_end,
                'line_items': validity_object.line_items.as_json,
                'source': 'rms_upload'
                })

            self.progress = int((count * 100.0) / total_count)

    def perform_delete_freight_rate_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
        data = self.data

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_freight_rates = list_fcl_freight_rates(filters = filters, return_query = True, page_limit = page_limit)['list']

        total_count = fcl_freight_rates.__sizeof__
        count = 0

        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                self.progress = int((count * 100.0) / total_count)
                continue

            delete_fcl_freight_rate({
                'id': freight.id,
                'performed_by_id': self.performed_by_id,
                'validity_start': data['validity_start'],
                'validity_end': data['validity_end'],
                'bulk_operation_id': self.id,
                'sourced_by_id': sourced_by_id,
                'procured_by_id': procured_by_id,
                'payment_term': data['payment_term']
            })

            self.progress = int((count * 100.0) / total_count)

    def perform_delete_local_rate_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
        data = self.data

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id })

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_freight_local_rates = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= page_limit)['list']

        total_count = fcl_freight_local_rates.__sizeof__
        count = 0

        for freight in fcl_freight_local_rates:
            count += 1

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                self.progress = int((count * 100.0) / total_count)
                continue

            delete_fcl_freight_rate({
                'id': freight.id,
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id,
                'sourced_by_id': sourced_by_id,
                'procured_by_id': procured_by_id
            })

            self.progress = int((count * 100.0) / total_count)

    def perform_add_freight_rate_markup_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
        data = self.data

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_freight_rates = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= page_limit)['list']

        total_count = fcl_freight_rates.__sizeof__
        count = 0

        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                self.progress = int((count * 100.0) / total_count)
                continue

            new_validities = []

            validities = [k for k in freight.validities if datetime.strptime(k['validity_end'], '%Y-%m-%d') >= datetime.date.today()]
            for validity_object in validities:
                if validity_object['validity_start'] > data['validity_end'] or validity_object['validity_end'] < data['validity_start']:
                    continue
                validity_object['validity_start'] = max(validity_object['validity_start'], data['validity_start'])
                validity_object['validity_end'] = min(validity_object['validity_end'], data['validity_end'])

                line_item = [t for t in validity_object['line_items'] if t['code'] == data['line_item_code']][0]
                if not line_item:
                    continue

                validity_object['line_items'].remove(line_item)

                if data['markup_type'].lower() == 'percent':
                    markup = float(data['markup'] * line_item['price']) / 100 
                else:
                    markup = data['markup']
                
                if data['markup_type'].lower() == 'net':
                    markup = client.ruby.get_money_exchange_for_fcl(data['markup_currency'], line_item['currency'], markup)

                line_item['price'] = line_item['price'] + markup

                if line_item['price'] < 0:
                    line_item['price'] = 0 
                
                validity_object['line_items'].append(line_item)

                validity_object['validity_start'] = max(datetime.strptime(validity_object.validity_start, '%Y-%m-%d'), datetime.date.today())

                new_validities.append(validity_object)

                for validity_object in new_validities:
                    create_fcl_freight_rate_data({
                        'origin_port_id': freight.origin_port_id,
                        'origin_main_port_id': freight.origin_main_port_id,
                        'destination_port_id': freight.destination_port_id,
                        'destination_main_port_id': freight.destination_main_port_id,
                        'container_size': freight.container_size,
                        'container_type': freight.container_type,
                        'commodity': freight.commodity,
                        'shipping_line_id': freight.shipping_line_id,
                        'importer_exporter_id': freight.importer_exporter_id,
                        'service_provider_id': freight.service_provider_id,
                        'cogo_entity_id': freight.cogo_entity_id,
                        'bulk_operation_id': self.id,
                        'performed_by_id': self.performed_by_id,
                        'sourced_by_id': sourced_by_id,
                        'procured_by_id': procured_by_id,
                        'validity_start': validity_object['validity_start'],
                        'validity_end': validity_object['validity_end'],
                        'line_items': validity_object['line_items'],
                        'source': 'rms_upload'
                    })
           
            self.progress = int((count * 100.0) / total_count)

    def perform_add_local_rate_markup_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
        data = self.data

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id })

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        local_rates = list_fcl_freight_rate_locals(filters= filters, return_query= True, page_limit= page_limit)['list']
        total_count = local_rates.__sizeof__
        count = 0

        for local in local_rates:
            count += 1

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                self.progress = int((count * 100.0) / total_count)
                continue

            line_items = [t for t in local['data']['line_items'] if t['code'] == data['line_item_code']]
            if not line_items:
                self.progress = int((count * 100.0) / total_count)

            local['data']['line_items'] = local['data']['line_items'] - line_items

            for line_item in line_items:
                if data['markup_type'].lower() == 'percent':
                    markup = float(data['markup'] * line_item['price']) / 100 
                else:
                    markup = data['markup']

                if data['markup_type'].lower() == 'net':
                    markup = client.ruby.get_money_exchange_for_fcl(data['markup_currency'], line_item['currency'], markup)

                line_item['price'] = line_item['price'] + markup

                if line_item['price'] < 0:
                    line_item['price'] = 0 

                for slab in line_item['slabs']:
                    if data['markup_type'].lower() == 'percent':
                        markup = float(data['markup'] * slab['price']) / 100 
                    else:
                        markup = data['markup']
                    
                    if data['markup_type'].lower() == 'net':
                        markup = client.ruby.get_money_exchange_for_fcl(data['markup_currency'], line_item['currency'], markup)

                    slab['price'] = slab['price'] + markup
                    if slab['price'] < 0:
                        slab['price'] = 0 
                
                local['data']['line_items'].append(line_item)

                update_fcl_freight_rate_local_data({
                    'id': local['id'],
                    'performed_by_id': self.performed_by_id,
                    'sourced_by_id': sourced_by_id,
                    'procured_by_id': procured_by_id,
                    'bulk_operation_id': self.id,
                    'data': local['data']
                })

                self.progress = int((count * 100.0) / total_count)

    def perform_update_free_days_limit_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
        data = self.data

        if data['slabs']:
            data['slabs'] = sorted(data.get('slabs', []), key=lambda slab: slab.get('lower_limit', 0))

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False })

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        free_days = list_fcl_freight_rate_free_days(filters= filters, return_query= True, page_limit= page_limit)['list']

        total_count = free_days.__sizeof__
        count = 0

        for free_day in free_days:
            count += 1

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                self.progress = int((count * 100.0) / total_count)
                continue

            update_fcl_freight_rate_free_day({
                'id': free_day.id,
                'performed_by_id': self.performed_by_id,
                'sourced_by_id': sourced_by_id,
                'procured_by_id': procured_by_id,
                'free_limit': data['free_limit'],
                'slabs': data['slabs'],
                'bulk_operation_id': self.id
            })

            self.progress = int((count * 100.0) / total_count)

    def perform_add_freight_line_item_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
        data = self.data

        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_freight_rates = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= page_limit)['list']

        total_count = fcl_freight_rates.__sizeof__
        count = 0

        new_line_item = {key: value for key, value in data if key.items() in ['code', 'unit', 'price', 'currency']}

        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                self.progress = int((count * 100.0) / total_count)
                continue

            new_validities = []

            validities = [k for k in freight.validities if datetime.strptime(k['validity_end'], '%Y-%m-%d') >= datetime.date.today()]

            for validity_object in validities:
                if validity_object['validity_start'] > data['validity_end'] or validity_object['validity_end'] < data['validity_start']:
                    continue
                validity_object['validity_start'] = max(validity_object['validity_start'], data['validity_start'])
                validity_object['validity_end'] = min(validity_object['validity_end'], data['validity_end'])

                line_item = [t for t in validity_object['line_items'] if t['code'] == data['line_item_code']][0]
                if not line_item:
                    continue

                validity_object['line_items'].remove(line_item)

                if data['markup_type'].lower() == 'percent':
                    markup = float(data['markup'] * line_item['price']) / 100 
                else:
                    markup = data['markup']
                
                if data['markup_type'].lower() == 'net':
                    markup = client.ruby.get_money_exchange_for_fcl(data['markup_currency'], line_item['currency'], markup)

                line_item['price'] = line_item['price'] + markup

                if line_item['price'] < 0:
                    line_item['price'] = 0 
                
                validity_object['line_items'].append(new_line_item)

                validity_object['validity_start'] = max(datetime.strptime(validity_object.validity_start, '%Y-%m-%d'), datetime.date.today())

                new_validities.append(validity_object)

                for validity_object in new_validities:
                    create_fcl_freight_rate_data({
                        'origin_port_id': freight.origin_port_id,
                        'origin_main_port_id': freight.origin_main_port_id,
                        'destination_port_id': freight.destination_port_id,
                        'destination_main_port_id': freight.destination_main_port_id,
                        'container_size': freight.container_size,
                        'container_type': freight.container_type,
                        'commodity': freight.commodity,
                        'shipping_line_id': freight.shipping_line_id,
                        'importer_exporter_id': freight.importer_exporter_id,
                        'service_provider_id': freight.service_provider_id,
                        'cogo_entity_id': freight.cogo_entity_id,
                        'bulk_operation_id': self.id,
                        'performed_by_id': self.performed_by_id,
                        'sourced_by_id': sourced_by_id,
                        'procured_by_id': procured_by_id,
                        'validity_start': validity_object['validity_start'],
                        'validity_end': validity_object['validity_end'],
                        'line_items': validity_object['line_items'],
                        'source': 'rms_upload'
                    })

            self.progress = int((count * 100.0) / total_count)

    def perform_update_free_days_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
        data = self.data

        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id })

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        local_rates = list_fcl_freight_rate_locals(filters= filters, return_query= True, page_limit= page_limit)['list']

        total_count = local_rates.__sizeof__
        count = 0

        for local in local_rates:
            count += 1

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                self.progress = int((count * 100.0) / total_count)
                continue

            update_fcl_freight_rate_free_day({
                'id': local.id,
                'performed_by_id': self.performed_by_id,
                'procured_by_id': procured_by_id,
                'sourced_by_id': sourced_by_id,
                'bulk_operation_id': self.id,
                'data': { data['free_days_type']: {key: value for key, value in data.items() if key in ['free_limit', 'slabs']}}
            })

            self.progress = int((count * 100.0) / total_count)

    def perform_update_commodity_surcharge_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
        data = self.data

        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_freight_rates = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= page_limit)['list']

        total_count = fcl_freight_rates.__sizeof__
        count = 0

        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                self.progress = int((count * 100.0) / total_count)
                continue

            update_fcl_freight_rate_data({
                'id': freight.id,
                'performed_by_id': self.performed_by_id,
                'procured_by_id': procured_by_id,
                'sourced_by_id': sourced_by_id,
                'bulk_operation_id': self.id,
                'commodity_surcharge_price': data['price'],
                'commodity_surcharge_currency': data['currency']
            })

            self.progress = int((count * 100.0) / total_count)

    def perform_update_weight_limit_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
        data = self.data

        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_freight_rates = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= page_limit)['list']

        weight_limit = {key: value for key, value in data.items() if key in ['free_limit', 'slabs']}

        total_count = fcl_freight_rates.__sizeof__
        count = 0

        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                self.progress = int((count * 100.0) / total_count)
                continue

            update_fcl_freight_rate_data({
                'id': freight.id,
                'performed_by_id': self.performed_by_id,
                'procured_by_id': procured_by_id,
                'sourced_by_id': sourced_by_id,
                'bulk_operation_id': self.id,
                'weight_limit': weight_limit
            })

            self.progress = int((count * 100.0) / total_count)

    def perform_extend_freight_rate_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
        data = self.data

        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_freight_rates = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= page_limit)['list']


        total_count = fcl_freight_rates.__sizeof__
        count = 0

        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                self.progress = int((count * 100.0) / total_count)
                continue

            validities = [k for k in freight.validities if datetime.strptime(k['validity_end'], '%Y-%m-%d') >= datetime.date.today()]

            if not validities:
                self.progress = int((count * 100.0) / total_count)
                continue

            create_params = {key: value for key, value in freight.__dict__.items() if key in ['origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'cogo_entity_id']}

            create_params['performed_by_id'] = self.performed_by_id
            create_params['sourced_by_id'] = sourced_by_id
            create_params['procured_by_id'] = procured_by_id
            create_params['cogo_entity_id'] = cogo_entity_id

            for validity_object in validities:
                create_params['validity_start'] = validity_object['validity_start']
                create_params['validity_end'] = validity_object['validity_end']
                create_params['line_items'] = validity_object['line_items']

                line_item = [t for t in validity_object['line_items'] if t['code'] == data['line_item_code']][0]
                if not line_item:
                    continue

                validity_object['line_items'].remove(line_item)

                if data['markup_type'].lower() == 'percent':
                    markup = float(data['markup'] * line_item['price']) / 100 
                else:
                    markup = data['markup']

                if data['markup_type'].lower() == 'net':
                    markup = client.ruby.get_money_exchange_for_fcl(data['markup_currency'], line_item['currency'], markup)

                line_item['price'] = line_item['price'] + markup

                if line_item['price'] < 0:
                    line_item['price'] = 0

                validity_object['line_items'].append(line_item)

                create_params['validity_start'] = max(datetime.strptime(validity_object.validity_start, '%Y-%m-%d'), datetime.date.today())

                for commodity in data['commodities']:
                    create_fcl_freight_rate_data(create_params.update({ 'commodity': commodity, 'source': 'rms_upload' }))

                for container_size in data['container_sizes']:
                    create_fcl_freight_rate_data(create_params.update({ 'container_size': container_size, 'source': 'rms_upload' }))

                for container_type in data['container_types']:
                    create_fcl_freight_rate_data(create_params.update({ 'container_type': container_type, 'source': 'rms_upload' }))

                create_audit(self,self.id)

                self.progress = int((count * 100.0) / total_count)

def create_audit(self,id):
    audit_data = {key: value for key,value in self if key not in ['id']}

    FclFreightRateAudit.create(
        bulk_operation_id = self.get('bulk_operation_id'),
        rate_sheet_id = self.get('rate_sheet_id'),
        action_name = 'create',
        performed_by_id = self['performed_by_id'],
        procured_by_id = self['procured_by_id'],
        sourced_by_id = self['sourced_by_id'],
        data = audit_data,
        object_id = id,
        object_type = 'FclFreightRate'
    )

def perform_extend_freight_rate_to_icds_action(self, sourced_by_id, procured_by_id, cogo_entity_id = None):
    data = self.data

    filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })

    page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

    fcl_freight_rate = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= page_limit)['list']

    validities = [k for k in fcl_freight_rate.validities if datetime.strptime(k['validity_end'], '%Y-%m-%d') >= datetime.date.today()]

    if not validities or FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
        self.progress = 100
        return

    if data['origin_port_ids']:
        origin_port_ids = data['origin_port_ids']
    else:
        origin_port_ids = [fcl_freight_rate.origin_port_id]

    if data['destination_port_ids']:
        destination_port_ids = data['destination_port_ids']
    else:
        destination_port_ids = [fcl_freight_rate.destination_port_id]

    total_count = origin_port_ids.__sizeof__ * destination_port_ids.__sizeof__ * validities.__sizeof__
    count = 0

    create_params = {key: value for key, value in fcl_freight_rate.items() if key in ['container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'cogo_entity_id']}
    create_params['performed_by_id'] = self.performed_by_id
    create_params['sourced_by_id'] = sourced_by_id
    create_params['procured_by_id'] = procured_by_id
    create_params['cogo_entity_id'] = cogo_entity_id

    for validity_object in validities:
        create_params['validity_start'] = validity_object['validity_start']
        create_params['validity_end'] = validity_object['validity_end']
        create_params['line_items'] = validity_object['line_items']

        create_params['validity_start'] = max(datetime.strptime(validity_object.validity_start, '%Y-%m-%d'), datetime.date.today())

        line_item = [t for t in validity_object['line_items'] if t['code'] == data['line_item_code']][0]

        if not line_item:
            count += (origin_port_ids.__sizeof__ * destination_port_ids.__sizeof__)
            self.progress = int((count * 100.0) / total_count)

        validity_object['line_items'].remove(line_item)

        if data['markup_type'].lower() == 'percent':
             markup = float(data['markup'] * line_item['price']) / 100 
        else:
            markup = data['markup']

        if data['markup_type'].lower() == 'net':
            markup = client.ruby.get_money_exchange_for_fcl(data['markup_currency'], line_item['currency'], markup)

        line_item['price'] = line_item['price'] + markup
        
        if line_item['price'] < 0:
            line_item['price'] = 0
        
        validity_object['line_items'].append(line_item)

        for origin_port_id in origin_port_ids:
            for destination_port_id in destination_port_ids:
                count += 1
                self.progress = int((count * 100.0) / total_count)

                if (origin_port_id == fcl_freight_rate.origin_port_id) and (destination_port_id == fcl_freight_rate.destination_port_id):
                    continue

                create_params['origin_port_id'] = origin_port_id
                if origin_port_id != fcl_freight_rate.origin_port_id:
                    create_params['origin_main_port_id'] = fcl_freight_rate.origin_port_id

                create_params['destination_port_id'] = destination_port_id
                if destination_port_id != fcl_freight_rate.destination_port_id:
                    create_params['destination_main_port_id'] = fcl_freight_rate.destination_port_id

                create_fcl_freight_rate_data(create_params.update({'source': 'rms_upload'}))