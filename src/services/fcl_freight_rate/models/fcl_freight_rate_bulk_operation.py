from database.db_session import db
from peewee import * 
import json
from playhouse.postgres_ext import *
from micro_services.client import *
from fastapi import HTTPException
from datetime import datetime,timedelta
from configs.definitions import FCL_FREIGHT_CHARGES, FCL_FREIGHT_LOCAL_CHARGES
from configs.global_constants import FREE_DAYS_TYPES, ALL_COMMODITIES, CONTAINER_SIZES, CONTAINER_TYPES, MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT
from configs.fcl_freight_rate_constants import DEFAULT_RATE_TYPE
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate import delete_fcl_freight_rate
from services.fcl_freight_rate.interaction.create_fcl_freight_rate import create_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_local import update_fcl_freight_rate_local
from services.fcl_freight_rate.interaction.update_fcl_freight_rate_free_day import update_fcl_freight_rate_free_day
from services.fcl_freight_rate.interaction.update_fcl_freight_rate import update_fcl_freight_rate_data
from services.fcl_freight_rate.interaction.list_fcl_freight_rates import list_fcl_freight_rates
from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_locals import list_fcl_freight_rate_locals
from services.fcl_freight_rate.interaction.list_fcl_freight_rate_free_days import list_fcl_freight_rate_free_days
from services.fcl_freight_rate.models.fcl_freight_rate_audit import FclFreightRateAudit
from services.fcl_freight_rate.interaction.delete_fcl_freight_rate_local import delete_fcl_freight_rate_local
from services.fcl_freight_rate.helpers.fcl_freight_rate_bulk_operation_helpers import get_relevant_rate_ids_from_audits_for_rate_sheet, get_relevant_rate_ids_for_extended_from_object,is_price_in_range,get_rate_sheet_id, get_progress_percent, get_common_create_params
from services.fcl_freight_rate.interaction.get_suggested_cogo_assured_fcl_freight_rates import get_suggested_cogo_assured_fcl_freight_rates
from fastapi.encoders import jsonable_encoder
from database.db_session import rd
from libs.parse_numeric import parse_numeric
from services.fcl_freight_rate.helpers.adjust_markup_price import adjusted_price_for_flash_booking
from services.fcl_freight_rate.interaction.update_schedule_in_fcl_freight_rate import update_schedule_in_fcl_freight_rate


ACTION_NAMES = ['extend_validity', 'delete_freight_rate', 'add_freight_rate_markup', 'add_local_rate_markup', 'update_free_days_limit', 'add_freight_line_item', 'update_free_days', 'update_weight_limit', 'extend_freight_rate', 'extend_freight_rate_to_icds', 'delete_local_rate','add_local_conditions','delete_local_rate_line_item', 'add_sailing_schedules']
MARKUP_TYPES = ['net','percent','absolute']
BATCH_SIZE = 1000

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateBulkOperation(BaseModel):
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
        table_name = 'fcl_freight_rate_bulk_operations'

    progress_percent_hash = "bulk_operation_progress"

    def progress_percent_key(self):
        return f"bulk_operations_{self.id}"
    
    def total_affected_rates_key(self):
        return f"bulk_operations_affected_{self.id}"

    def set_progress_percent(self,progress_percent):
        if rd:
            rd.hset(self.progress_percent_hash, self.progress_percent_key(), progress_percent)
    
    def set_total_affected_rates(self,total_affected_rates):
        if rd:
            rd.hset(self.progress_percent_hash, self.total_affected_rates_key(), total_affected_rates)

    def validate_action_name(self):
        if self.action_name not in ACTION_NAMES:
            raise HTTPException(status_code=400,detail='Invalid action Name')
    
    def validate_extend_validity_data(self):
        data = self.data
        
        if self.sourced_by_id is None or self.procured_by_id is None:
             raise HTTPException(status_code=400, detail='procured_by_id and sourced_by_id cannot be None')
           
        if data.get('markup') and data.get('markup_type') and data['markup_type'] not in MARKUP_TYPES:
            raise HTTPException(status_code=400, detail='markup_type is invalid')
        
        if data['validity_end'].date() < datetime.now().date():
            raise HTTPException(status_code=400, detail='validity_end cannot be less than current date')
        
        if data['validity_end'].date() > (datetime.now() +timedelta(days=60)).date():
            raise HTTPException(status_code=400, detail='validity_end cannot be greater than 60 days')
        data['validity_end'] = data['validity_end'].strftime('%Y-%m-%d')

    def validate_delete_freight_rate_data(self):
        data = self.data

        if self.sourced_by_id is None or self.procured_by_id is None:
            raise HTTPException(status_code=400, detail='procured_by_id and sourced_by_id cannot be None')
        
        if data['validity_end'] < data['validity_start']:
            raise HTTPException(status_code=400, detail='validity_end cannot be less than validity start')
        
        if data.get('rates_greater_than_price')!=None and data.get('rates_greater_than_price')!=None and data['rates_greater_than_price'] > data['rates_less_than_price']:
            raise HTTPException(status_code=400, detail='Greater than price cannot be greater than Less than price')
        
        if data.get('rate_sheet_serial_id'):
            rate_sheet_id = get_rate_sheet_id(data.get('rate_sheet_serial_id'))
            if not rate_sheet_id:
                raise HTTPException(status_code=400, detail='Invalid Rate sheet serial id') 
        
        data['validity_start'] = data['validity_start'].strftime('%Y-%m-%d')
        data['validity_end'] = data['validity_end'].strftime('%Y-%m-%d')

        
    def validate_delete_local_rate_data(self):

        if self.sourced_by_id is None or self.procured_by_id is None:
             raise HTTPException(status_code=400, detail='procured_by_id and sourced_by_id cannot be None')
        
        return True
    
    def validate_add_freight_rate_markup_data(self):
        data = self.data

        if self.sourced_by_id is None or self.procured_by_id is None:
            raise HTTPException(status_code=400, detail='procured_by_id and sourced_by_id cannot be None')

        if float(data['markup']) == 0:
            raise HTTPException(status_code=400, detail='markup cannot be 0')

        if data['markup_type'] not in MARKUP_TYPES:
            raise HTTPException(status_code=400, detail='markup_type is invalid')
        
        if data['validity_end'].date() < datetime.now().date():
            raise HTTPException(status_code=400, detail='validity_end cannot be less than current date')
        
        if data['validity_end'].date() < data['validity_start'].date():
            raise HTTPException(status_code=400, detail='validity_end cannot be less than validity start')
        
        if data.get('rates_greater_than_price')!=None and data.get('rates_greater_than_price')!=None and data['rates_greater_than_price'] > data['rates_less_than_price']:
            raise HTTPException(status_code=400, detail='Greater than price cannot be greater than Less than price')
        
        if data.get('rate_sheet_serial_id'):
            rate_sheet_id = get_rate_sheet_id(data.get('rate_sheet_serial_id'))
            if not rate_sheet_id:
                raise HTTPException(status_code=400, detail='Invalid Rate sheet serial id') 
            
        fcl_freight_charges_dict = FCL_FREIGHT_CHARGES.get()

        charge_codes = fcl_freight_charges_dict.keys()

        if data['line_item_code'] not in charge_codes:
            raise HTTPException(status_code=400, detail='line_item_code is invalid')

        
        data['validity_start'] = data['validity_start'].strftime('%Y-%m-%d')
        data['validity_end'] = data['validity_end'].strftime('%Y-%m-%d')
        
        
    def validate_add_local_rate_markup_data(self):
        data = self.data

        if self.sourced_by_id is None or self.procured_by_id is None:
            raise HTTPException(status_code=400, detail='procured_by_id and sourced_by_id cannot be None')

        if float(data['markup']) == 0:
            raise HTTPException(status_code=400, detail='markup cannot be 0')

        if data['markup_type'] not in MARKUP_TYPES:
            raise HTTPException(status_code=400, detail='markup_type is invalid')
        
        fcl_freight_charges_dict = FCL_FREIGHT_CHARGES.get()

        charge_codes = fcl_freight_charges_dict.keys()

        if data['line_item_code'] not in charge_codes:
            raise HTTPException(status_code=400, detail='line_item_code is invalid')
        
        if str(data['markup_type']).lower() == 'percent':
            return

    def validate_delete_local_rate_line_item_data(self):
        data = self.data
        
        fcl_freight_charges_dict = FCL_FREIGHT_LOCAL_CHARGES.get()

        charge_codes = fcl_freight_charges_dict.keys()

        if data['line_item_code'] not in charge_codes:
            raise HTTPException(status_code=400, detail='line_item_code is invalid')
        
    def validate_add_local_conditions_data(self):
        data = self.data
        
        fcl_freight_charges_dict = FCL_FREIGHT_LOCAL_CHARGES.get()

        charge_codes = fcl_freight_charges_dict.keys()
        line_items = data['line_items']

        for line_item in line_items:
            if line_item['code'] not in charge_codes:
                raise HTTPException(status_code=400, detail='line_item_code is invalid')
        
        
    def validate_update_free_days_limit_data(self):
        data = self.data

        if self.sourced_by_id is None or self.procured_by_id is None:
            raise HTTPException(status_code=400, detail='procured_by_id and sourced_by_id cannot be None')

        if int(data['free_limit']) <= 0:
            raise HTTPException(status_code=400, detail='free_limit cannot be less than or equal to 0')
        
        slabs = sorted(data.get('slabs', []), key=lambda slab: slab.get('lower_limit', 0))

        if any(slab.get('upper_limit', 0) <= slab.get('lower_limit', 0) for slab in slabs):
            raise HTTPException(status_code=400, detail='slabs is invalid')

        if slabs[0] and (int(slabs[0]['lower_limit']) <= int(data['free_limit'])):
            raise HTTPException(status_code=400, detail='slabs lower limit should be greater than free limit')

        if any(index > 0 and slab.get('lower_limit', 0) <= slabs[index - 1].get('upper_limit', 0) for index, slab in enumerate(slabs)):
            raise HTTPException(status_code=400, detail='slabs is invalid')

    def validate_add_freight_line_item_data(self):
        data = self.data

        if self.sourced_by_id is None or self.procured_by_id is None:
            raise HTTPException(status_code=400, detail='procured_by_id and sourced_by_id cannot be None')

        fcl_freight_charges_dict = FCL_FREIGHT_CHARGES.get()

        code_config = fcl_freight_charges_dict[data['code']]
        if not code_config:
            raise HTTPException(status_code=400, detail='code is invalid')
        
        if data['units'] not in code_config['units']:
            raise HTTPException(status_code=400, detail='unit is invalid')
        
        if data['validity_end'] < datetime.now():
            raise HTTPException(status_code=400, detail='validity_end cannot be less than current date')
        
        if data['validity_end'] < data['validity_start']:
            raise HTTPException(status_code=400, detail='validity_end cannot be less than validity start')
        data['validity_start'] = data['validity_start'].strftime('%Y-%m-%d')
        data['validity_end'] = data['validity_end'].strftime('%Y-%m-%d')
        
    def validate_update_free_days_data(self):
        data = self.data

        if self.sourced_by_id is None or self.procured_by_id is None:
            raise HTTPException(status_code=400, detail='procured_by_id and sourced_by_id cannot be None')

        if data['free_days_type'] not in FREE_DAYS_TYPES:
            raise HTTPException(status_code=400, detail='free_days_type is invalid')
        
        if int(data['free_limit']) <= 0:
            raise HTTPException(status_code=400, detail='free_limit cannot be less than or equal to 0')
        
        slabs = sorted(data.get('slabs', []), key=lambda slab: slab.get('lower_limit', 0))

        if any(slab.get('upper_limit', 0) <= slab.get('lower_limit', 0) for slab in slabs):
            raise HTTPException(status_code=400, detail='slabs is invalid')

        if len(slabs)>0 and (int(slabs[0]['lower_limit']) <= int(data['free_limit'])):
            raise HTTPException(status_code=400, detail='slabs lower limit should be greater than free limit')

        if any(index > 0 and slab.get('lower_limit', 0) <= slabs[index - 1].get('upper_limit', 0) for index, slab in enumerate(slabs)):
            raise HTTPException(status_code=400, detail='slabs is invalid')

    def validate_update_weight_limit_data(self):
        data = self.data

        if self.sourced_by_id is None or self.procured_by_id is None:
            raise HTTPException(status_code=400, detail='procured_by_id and sourced_by_id cannot be None')

        if int(data['free_limit']) <= 0:
            raise HTTPException(status_code=400, detail='free_limit cannot be less than or equal to 0')
        
        slabs = sorted(data.get('slabs', []), key=lambda slab: slab.get('lower_limit', 0))

        if any(slab.get('upper_limit', 0) <= slab.get('lower_limit', 0) for slab in slabs):
            raise HTTPException(status_code=400, detail='slabs is invalid')

        if len(slabs)>0 and (int(slabs[0]['lower_limit']) <= int(data['free_limit'])):
            raise HTTPException(status_code=400, detail='slabs lower limit should be greater than free limit')\

        if any(index > 0 and slab.get('lower_limit', 0) <= slabs[index - 1].get('upper_limit', 0) for index, slab in enumerate(slabs)):
            raise HTTPException(status_code=400, detail='slabs is invalid')

    def validate_extend_freight_rate_data(self):
        data = self.data

        if self.sourced_by_id is None or self.procured_by_id is None:
            raise HTTPException(status_code=400, detail='procured_by_id and sourced_by_id cannot be None')
        
        if data.get("extend_for_flash_booking"):
            return


        if  [x for x in data['commodities'] if x not in ALL_COMMODITIES]!=[]:
            raise HTTPException(status_code=400, detail='commodities is invalid')
        
        if  [x for x in data['container_sizes'] if x not in CONTAINER_SIZES]!=[]:
            raise HTTPException(status_code=400, detail='container_sizes is invalid')
        if  [x for x in data['container_types'] if x not in CONTAINER_TYPES]!=[]:
            raise HTTPException(status_code=400, detail='container_types is invalid')
        
        if data['markup_type'] not in MARKUP_TYPES:
            raise HTTPException(status_code=400, detail='markup_type is invalid')

        
    def validate_extend_freight_rate_to_icds_data(self):
        data = self.data

        if self.sourced_by_id is None or self.procured_by_id is None:
            raise HTTPException(status_code=400, detail='procured_by_id and sourced_by_id cannot be None')

        if data['markup_type'] not in MARKUP_TYPES:
            raise HTTPException(status_code=400, detail='markup_type is invalid')
    
        
        if self.data['origin_port_ids'] or self.data['destination_port_ids']:
            rate_id = data['filters']['id']
            if not rate_id:
                raise HTTPException(status_code=400, detail='rate_id is not present')
            
            if not isinstance(rate_id, str):
                rate_id = rate_id[0]

            rate = FclFreightRate.get_or_none(id=rate_id)
            # locations = maps.list_locations({'filters': { 'id': [str(rate.origin_port_id), str(rate.destination_port_id)] }, 'includes': { 'icd_ports': {} }})['list']
            # origin_icd_location = [t for t in locations if t['id'] == rate.origin_port_id][0]['icd_ports']['id']
            
            # destination_icd_location = [t for t in locations if t['id']== rate.destination_port_id][0]['icd_ports']['id']
            # if [t for t in self.data['origin_port_ids']if t not in  origin_icd_location] != [None]:
            #     raise HTTPException(status_code=400, detail='origin_icd_port_id is invalid')
            
            # if [t for t in self.data['destination_port_ids']if t not in  destination_icd_location] != None:
            #     raise HTTPException(status_code=400, detail='destination_icd_port_id is invalid')
    def validate_add_sailing_schedules_data(self):
        data = self.data
        
        if data['validity_end'].date() < datetime.now().date():
            raise HTTPException(status_code=400, detail='validity_end cannot be less than current date')
        
        if data['validity_end'].date() < data['validity_start'].date():
            raise HTTPException(status_code=400, detail='validity_end cannot be less than validity start') 
        
        data['validity_start'] = data['validity_start'].strftime('%Y-%m-%d')
        data['validity_end'] = data['validity_end'].strftime('%Y-%m-%d')        


    def perform_batch_extend_validity_action(self, batch_query,  count , total_count, total_affected_rates, sourced_by_id, procured_by_id):
        data = self.data 
        sourced_by_ids = data.get('sourced_by_ids')
        procured_by_ids = data.get('procured_by_ids')
        
        fcl_freight_rates = jsonable_encoder(list(batch_query.dicts()))
        
        for freight in fcl_freight_rates:
            count += 1
            try:
                actual_sourced_by_id = sourced_by_ids[freight['id']]
            except:
                actual_sourced_by_id = None
            
            try:
                actual_procured_by_id = procured_by_ids[freight['id']]
            except:
                actual_procured_by_id = None
 
            validity_object = None
            for t in freight["validities"]:
                if datetime.strptime(t['validity_end'],'%Y-%m-%d') < datetime.strptime(data['validity_end'],'%Y-%m-%d'):
                    validity_object = t

            if not validity_object:
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue
            
            if FclFreightRateAudit.get_or_none(bulk_operation_id=self.id,object_id=freight['id']):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            if data.get('markup'):
                line_items = [t for t in validity_object['line_items'] if t['code'] == data['line_item_code']]

                if line_items:
                    line_item = line_items[0]
                    validity_object['line_items'].remove(line_item)
                    
                    if data['markup_type'].lower() == 'percent':
                        markup = float(data['markup'] * line_item['price']) / 100 
                    else:
                        markup = data['markup']
                    
                    if data['markup_type'].lower() == 'net':
                        markup = common.get_money_exchange_for_fcl({'from_currency': data['markup_currency'], 'to_currency': line_item['currency'], 'price': markup}).get('price')

                    if data['markup_type'].lower() == 'absolute':
                        line_item['price'] = markup
                        line_item['market_price'] = markup
                        line_item['currency'] = data['markup_currency']
                    else:
                        line_item['price'] = line_item['price'] + markup
                        line_item['market_price'] = line_item['price'] if not line_item.get('market_price') else line_item['market_price'] + markup
                        
                    
                    validity_object['line_items'].append(line_item)


            validity_start = max(datetime.strptime(validity_object['validity_start'], '%Y-%m-%d'), datetime.now())
            validity_end = min(datetime.strptime(data['validity_end'], '%Y-%m-%d'), (datetime.now() + timedelta(days=45)))
            

            if actual_sourced_by_id:
                sourced_by_id_data = actual_sourced_by_id 
            else:
                sourced_by_id_data = sourced_by_id 

            if actual_procured_by_id:
                procured_by_id_data = actual_procured_by_id
            else:
                procured_by_id_data = procured_by_id
                
            
            freight_rate_object = {
                        'origin_port_id': freight["origin_port_id"],
                        'origin_main_port_id': freight['origin_main_port_id'],
                        'destination_port_id': freight["destination_port_id"],
                        'destination_main_port_id': freight['destination_main_port_id'],
                        'container_size': freight["container_size"],
                        'container_type': freight["container_type"],
                        'commodity': freight["commodity"],
                        'shipping_line_id': freight["shipping_line_id"],
                        'importer_exporter_id': freight["importer_exporter_id"] if freight['importer_exporter_id'] else None,
                        'service_provider_id': freight["service_provider_id"] if freight['service_provider_id'] else None,
                        'cogo_entity_id': freight["cogo_entity_id"] if freight['cogo_entity_id'] else None,
                        'bulk_operation_id': self.id,
                        'performed_by_id': self.performed_by_id,
                        'sourced_by_id': sourced_by_id_data ,
                        'procured_by_id': procured_by_id_data,
                        'validity_start':validity_start,
                        'validity_end': validity_end,
                        'line_items': validity_object['line_items'],
                        'rate_type': freight['rate_type'],
                        'source': 'bulk_operation',
                        'mode': freight['mode'],
                        'rate_sheet_validation': True,
                    }
            create_fcl_freight_rate_data(freight_rate_object)
            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_total_affected_rates(total_affected_rates)
            self.set_progress_percent(progress)
            
        return count, total_affected_rates
        
    def perform_extend_validity_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        data = self.data
        total_affected_rates = 0

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })
        
        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']
        
        includes = { 
                    'id': True,
                    'validities': True,
                    'origin_port_id': True,
                    'origin_main_port_id': True,
                    'destination_port_id': True,
                    'destination_main_port_id': True,
                    'container_size': True,
                    'container_type': True,
                    'commodity': True,
                    'shipping_line_id': True,
                    'importer_exporter_id': True,
                    'service_provider_id': True,
                    'cogo_entity_id': True,
                    'rate_type': True,
                    'mode': True,
                }
       
        query = list_fcl_freight_rates(filters = filters, return_query = True, page_limit = None, includes = includes, sort_by=None)['list']

        total_count = query.count()
        count = 0
        
        while count < total_count:
            batch_query = query.limit(BATCH_SIZE)
            if not batch_query.exists():
                break 
            count, total_affected_rates = self.perform_batch_extend_validity_action(batch_query, count , total_count, total_affected_rates, sourced_by_id, procured_by_id)
        
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save() 
            
            
    def perform_batch_delete_freight_rate_action(self, batch_query,  count , total_count, total_affected_rates, sourced_by_id, procured_by_id):
        data = self.data
        fcl_freight_rates = list(batch_query.dicts())
        validity_start = datetime.strptime(data['validity_start'], "%Y-%m-%d")
        validity_end = datetime.strptime(data['validity_end'], "%Y-%m-%d")
            
        if data.get('delete_all_validities') == True:
            validity_start -= timedelta(days=60)
            validity_end += timedelta(days=60)
            
        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.get_or_none(bulk_operation_id=self.id,object_id=freight["id"]):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue           

            delete_fcl_freight_rate({
                'id': str(freight["id"]),
                'performed_by_id': self.performed_by_id,
                'validity_start': validity_start,
                'validity_end': validity_end,
                'bulk_operation_id': self.id,
                'sourced_by_id': sourced_by_id,
                'procured_by_id': procured_by_id,
                'payment_term': data.get('payment_term'),
                'rate_type': data.get('rate_type', DEFAULT_RATE_TYPE),
                'rates_greater_than_price':data.get('rates_greater_than_price'),
                'rates_less_than_price':data.get('rates_less_than_price'),
                'comparison_charge_code':data.get('comparison_charge_code'),
                'comparison_currency':data.get('comparison_currency')
            })
            progress = int((count * 100.0) / total_count)
            total_affected_rates += 1
            self.set_total_affected_rates(total_affected_rates)
            self.set_progress_percent(progress)
        return count, total_affected_rates

    def perform_delete_freight_rate_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        data = self.data
        total_affected_rates = 0

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })

        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']

        rate_sheet_id=get_rate_sheet_id(data.get('rate_sheet_serial_id'))
        rate_ids = []
        rate_ids += get_relevant_rate_ids_from_audits_for_rate_sheet(rate_sheet_id)
        
        if filters.get('id'):
            object_ids = rate_ids + (filters['id'] if isinstance(filters['id'], list) else [filters.get('id')])
        else:
            object_ids = rate_ids
            
        rate_ids += get_relevant_rate_ids_for_extended_from_object(data['apply_to_extended_rates'], object_ids)
        
        if rate_ids:
            if isinstance(filters.get('id'), list):
                rate_ids += filters['id']
            elif filters.get('id'):
                rate_ids += [filters['id']]
            filters['id'] = rate_ids
                      
                  
        includes = {'id': True}
        
        query = list_fcl_freight_rates(filters = filters, return_query = True, page_limit = None, includes=includes, sort_by="id")['list']

        total_count = query.count()
        count = 0
        offset = 0
        
        while(offset < total_count):
            batch_query = query.offset(offset).limit(BATCH_SIZE)
            offset += BATCH_SIZE
            count, total_affected_rates = self.perform_batch_delete_freight_rate_action(batch_query,  count , total_count, total_affected_rates, sourced_by_id, procured_by_id)

        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else  get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()  



    def perform_delete_local_rate_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        data = self.data
        total_affected_rates = 0
        
        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id })

        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']

        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_freight_local_rates = list_fcl_freight_rate_locals(filters= filters, return_query= True, page_limit= page_limit)['list']
        total_count = len(fcl_freight_local_rates)
        count = 0

        for freight in fcl_freight_local_rates:
            count += 1

            if FclFreightRateAudit.get_or_none(bulk_operation_id=self.id,object_id=freight["id"]):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            delete_fcl_freight_rate_local({
                'id': str(freight["id"]),
                'performed_by_id': self.performed_by_id,
                'bulk_operation_id': self.id,
                'sourced_by_id': sourced_by_id,
                'procured_by_id': procured_by_id
            })
            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_progress_percent(progress)
            
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else  get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()    



    def perform_batch_add_freight_rate_markup_action(self, batch_query, count , total_count, total_affected_rates, sourced_by_id, procured_by_id):
        data = self.data
        affect_market_price = data.get('affect_market_price', True)
        is_system_operation = data.get('is_system_operation', False)
        min_allowed_markup =  data.get('min_allowed_markup')
        max_allowed_markup =  data.get('max_allowed_markup')
        fcl_freight_rates = list(batch_query.dicts())
        
        validity_start = datetime.strptime(data['validity_start'], '%Y-%m-%d')
        validity_end = datetime.strptime(data['validity_end'], '%Y-%m-%d') 
        
        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.get_or_none(bulk_operation_id=self.id,object_id=freight["id"]):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            new_validities = []

            validities = [k for k in freight["validities"] if datetime.strptime(k['validity_end'], '%Y-%m-%d') >= datetime.now()]
            for validity_object in validities:
                validity_object['validity_start'] = datetime.strptime(validity_object['validity_start'], '%Y-%m-%d')
                validity_object['validity_end'] = datetime.strptime(validity_object['validity_end'], '%Y-%m-%d')

                if validity_object['validity_start'] > validity_end  or validity_object['validity_end'] < validity_start:
                    continue
                validity_object['validity_start'] = max(validity_object['validity_start'], validity_start)
                validity_object['validity_end'] = min(validity_object['validity_end'], validity_end)

                line_item = [t for t in validity_object['line_items'] if t['code'] == data['line_item_code']][0]
                if not line_item:
                    continue

                validity_object['line_items'].remove(line_item)

               
                if not is_price_in_range(data.get('rate_price_greater_than'),data.get('rate_price_less_than'), line_item['price'],data['markup_currency'],line_item['currency']):
                    continue
                
                if data['markup_type'].lower() == 'percent':
                    markup = float(data['markup'] * abs(line_item['price'])) / 100 
                    
                    if min_allowed_markup and max_allowed_markup:
                        if line_item['currency'] != data['markup_currency']:
                           min_allowed_markup =  common.get_money_exchange_for_fcl({'from_currency': data['markup_currency'] , 'to_currency': line_item['currency'] , 'price': min_allowed_markup}).get('price')
                           max_allowed_markup =  common.get_money_exchange_for_fcl({'from_currency': data['markup_currency'] , 'to_currency': line_item['currency'] , 'price': max_allowed_markup}).get('price')
                        markup = max(min_allowed_markup, min(markup, max_allowed_markup))
                        
                        if data.get('tag') == 'trend_GRI' and markup < 0:
                            min_allowed_price = line_item['market_price'] + min_allowed_markup 
                            
                            if  line_item['price'] < min_allowed_price:
                               continue
                            markup = max(markup, (min_allowed_price - line_item['price']))
                            
                else:
                    markup = data['markup']
                
                if data['markup_type'].lower() == 'net':
                    markup = common.get_money_exchange_for_fcl({'from_currency': data['markup_currency'], 'to_currency': line_item['currency'], 'price': markup}).get('price')

                if data['markup_type'].lower() == 'absolute':
                    line_item['price'] = markup
                    line_item['market_price'] = markup
                    line_item['currency'] = data['markup_currency']
                else:
                    line_item['price'] = line_item['price'] + markup
                    if affect_market_price:
                        line_item['market_price'] = line_item['price'] if not line_item.get('market_price') else line_item['market_price'] + markup
                    
                
                validity_object['line_items'].append(line_item)

                validity_object['validity_start'] = max(validity_object["validity_start"], datetime.now())

                new_validities.append(validity_object)
           
            if freight['rate_type']=='cogo_assured' and new_validities:
                freight_rate_object = get_common_create_params(data,self.id, self.performed_by_id,sourced_by_id, procured_by_id,freight,is_system_operation)
                price_params = {'price': new_validities[0]['line_items'][0].get('price'), 'currency': new_validities[0]['line_items'][0].get('currency')}
                response = get_suggested_cogo_assured_fcl_freight_rates(price_params)
                freight_rate_object['validities'] = response['data'].get('validities')
                freight_rate_object['weight_limit'] = freight['weight_limit']
                freight_rate_object['validity_start'] = validity_start
                freight_rate_object['validity_end'] = validity_end
                
                create_fcl_freight_rate_data(freight_rate_object)
               
                
            else:      
                for validity_object in new_validities:
                    freight_rate_object = get_common_create_params(data,self.id, self.performed_by_id,sourced_by_id, procured_by_id,freight,is_system_operation)
                    freight_rate_object['line_items'] = validity_object['line_items']
                    freight_rate_object['schedule_type'] = validity_object['schedule_type']
                    freight_rate_object['payment_term'] = validity_object['payment_term']
                    freight_rate_object['validity_start'] = validity_object['validity_start']
                    freight_rate_object['validity_end'] = validity_object['validity_end']
                    
                    create_fcl_freight_rate_data(freight_rate_object)

            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_total_affected_rates(total_affected_rates)
            self.set_progress_percent(progress)
        return count, total_affected_rates
        
        
        
    def perform_add_freight_rate_markup_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        total_affected_rates = 0
        data = self.data
                        
        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })
        
        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']

        rate_sheet_id=get_rate_sheet_id(data.get('rate_sheet_serial_id'))
        rate_ids = [] 
        rate_ids += get_relevant_rate_ids_from_audits_for_rate_sheet(rate_sheet_id)
        
        if filters.get('id'):
            object_ids = rate_ids + (filters['id'] if isinstance(filters['id'], list) else [filters.get('id')])
        else:
            object_ids = rate_ids

        rate_ids += get_relevant_rate_ids_for_extended_from_object(data['apply_to_extended_rates'],object_ids)
        
        
        if rate_ids:
            if isinstance(filters.get('id'), list):
                rate_ids += filters['id']
            elif filters.get('id'):
                rate_ids += [filters['id']]
            filters['id'] = rate_ids
            
        includes = { 
                    'id': True,
                    'validities': True,
                    'origin_port_id': True,
                    'origin_main_port_id': True,
                    'destination_port_id': True,
                    'destination_main_port_id': True,
                    'container_size': True,
                    'container_type': True,
                    'commodity': True,
                    'shipping_line_id': True,
                    'importer_exporter_id': True,
                    'service_provider_id': True,
                    'cogo_entity_id': True,
                    'rate_type': True,
                    'sourced_by_id': True,
                    'procured_by_id': True,
                    'mode': True,
                    'weight_limit': True
                }

        query = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= None, includes=includes, sort_by="id")['list']
        total_count = query.count()
        count = 0
        offset = 0

        while(offset < total_count):
            batch_query = query.offset(offset).limit(BATCH_SIZE)
            offset += BATCH_SIZE
            count, total_affected_rates = self.perform_batch_add_freight_rate_markup_action(batch_query, count , total_count, total_affected_rates, sourced_by_id, procured_by_id)
        
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else  get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()  


    def perform_add_local_rate_markup_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        data = self.data
        total_affected_rates = 0

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id })

        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']
        
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        local_rates = list_fcl_freight_rate_locals(filters= filters, return_query= True, page_limit= page_limit)['list']
        total_count = len(local_rates)
        count = 0

        for local in local_rates:
            count += 1

            if FclFreightRateAudit.get_or_none('bulk_operation_id' == self.id,object_id = local['id']):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            line_items = [t for t in local['data']['line_items'] if t['code'] == data['line_item_code']]
            if not line_items:
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)

            local['data']['line_items'] = local['data']['line_items'] - line_items

            for line_item in line_items:
                if data['markup_type'].lower() == 'percent':
                    markup = float(data['markup'] * line_item['price']) / 100 
                else:
                    markup = data['markup']

                if data['markup_type'].lower() == 'net':
                    markup = common.get_money_exchange_for_fcl({'from_currency': data['markup_currency'], 'to_currency': line_item['currency'], 'price': markup})['price']
                
                if data['markup_type'].lower() == 'absolute':
                    line_item['price'] = markup
                else:
                    line_item['price'] = line_item['price'] + markup

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
                
                local['data']['line_items'].append(line_item)

                update_fcl_freight_rate_local({
                    'id': local['id'],
                    'performed_by_id': self.performed_by_id,
                    'sourced_by_id': sourced_by_id,
                    'procured_by_id': procured_by_id,
                    'bulk_operation_id': self.id,
                    'data': local['data']
                })
            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_progress_percent(progress)
            
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()
        

    def perform_update_free_days_limit_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        total_affected_rates = 0
        data = self.data

        if data['slabs']:
            data['slabs'] = sorted(data.get('slabs', []), key=lambda slab: slab.get('lower_limit', 0))

        filters = (data['filters'] or {}) | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False })

        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']
        
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        free_days = list_fcl_freight_rate_free_days(filters= filters, return_query= True, page_limit= page_limit)['list']

        total_count = len(free_days)
        count = 0

        for free_day in free_days:
            count += 1

            if FclFreightRateAudit.get_or_none(bulk_operation_id=self.id,object_id=free_day['id']):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            update_fcl_freight_rate_free_day({
                'id': free_day['id'],
                'performed_by_id': self.performed_by_id,
                'sourced_by_id': sourced_by_id,
                'procured_by_id': procured_by_id,
                'free_limit': data['free_limit'],
                'slabs': data['slabs'],
                'bulk_operation_id': self.id
            })
            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_progress_percent(progress)
            
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()  

    def perform_add_freight_line_item_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        total_affected_rates = 0
        data = self.data

        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })
        
        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']
        
        includes = { 
                    'id': True,
                    'validities': True,
                    'origin_port_id': True,
                    'origin_main_port_id': True,
                    'destination_port_id': True,
                    'destination_main_port_id': True,
                    'container_size': True,
                    'container_type': True,
                    'commodity': True,
                    'shipping_line_id': True,
                    'importer_exporter_id': True,
                    'service_provider_id': True,
                    'cogo_entity_id': True,
                    'rate_type': True,
                    'mode': True,
                }

        fcl_freight_rates = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= None,includes=includes)['list']
        fcl_freight_rates = list(fcl_freight_rates.dicts())

        total_count = len(fcl_freight_rates)
        count = 0

        new_line_item = {key: value for key, value in data.items() if key in ['code', 'units', 'price', 'currency']}
        # data['validity_start'] = datetime.strptime(data['validity_start'], '%Y-%m-%d')
        # data['validity_end'] = datetime.strptime(data['validity_end'], '%Y-%m-%d')
        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.get_or_none(bulk_operation_id = self.id,object_id=freight['id']):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            new_validities = []

            validities = [k for k in freight["validities"] if k['validity_end'].date() >= datetime.now().date()]

            for validity_object in validities:
                validity_object['validity_start'] = datetime.strptime(validity_object['validity_start'], '%Y-%m-%d')
                validity_object['validity_end'] = datetime.strptime(validity_object['validity_end'], '%Y-%m-%d')

                if validity_object['validity_start'] > data['validity_end'] or validity_object['validity_end'] < data['validity_start']:
                    continue
                validity_object['validity_start'] = max(validity_object['validity_start'], data['validity_start'])
                validity_object['validity_end'] = min(validity_object['validity_end'], data['validity_end'])

                line_item = [t for t in validity_object['line_items'] if t['code'] == data['code']][0]
                if not line_item:
                    continue

                validity_object['line_items'].remove(line_item)
                
                validity_object['line_items'].append(new_line_item)

                validity_object['validity_start'] = max(validity_object['validity_start'], datetime.now())

                new_validities.append(validity_object)

                for validity_object in new_validities:
                    freight_rate_object = {
                        'origin_port_id': freight["origin_port_id"],
                        'origin_main_port_id': freight["origin_main_port_id"],
                        'destination_port_id': freight["destination_port_id"],
                        'destination_main_port_id': freight["destination_main_port_id"],
                        'container_size': freight["container_size"],
                        'container_type': freight["container_type"],
                        'commodity': freight["commodity"],
                        'shipping_line_id': freight["shipping_line_id"],
                        'importer_exporter_id': freight["importer_exporter_id"],
                        'service_provider_id': freight["service_provider_id"],
                        'cogo_entity_id': freight["cogo_entity_id"],
                        'bulk_operation_id': self.id,
                        'performed_by_id': self.performed_by_id,
                        'sourced_by_id': sourced_by_id,
                        'procured_by_id': procured_by_id,
                        'validity_start': validity_object['validity_start'],
                        'validity_end': validity_object['validity_end'],
                        'line_items': validity_object['line_items'],
                        'schedule_type': validity_object['schedule_type'],
                        'payment_term': validity_object['payment_term'],
                        'rate_type': freight['rate_type'],
                        'source': 'bulk_operation',
                        'mode': freight['mode']
                    }
                    
                    create_fcl_freight_rate_data(freight_rate_object)

            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_progress_percent(progress)
        
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()  


    def perform_update_free_days_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        data = self.data
        total_affected_rates = 0

        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id })

        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']
        
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        local_rates = list_fcl_freight_rate_locals(filters= filters, return_query= True, page_limit= page_limit)['list']

        total_count = len(local_rates)
        count = 0

        for local in local_rates:
            count += 1

            if FclFreightRateAudit.get_or_none(bulk_operation_id = self.id,object_id=local["id"]):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            update_fcl_freight_rate_local({
                'id': local["id"],
                'performed_by_id': self.performed_by_id,
                'procured_by_id': procured_by_id,
                'sourced_by_id': sourced_by_id,
                'bulk_operation_id': self.id,
                'data': { data['free_days_type']: {key: value for key, value in data.items() if key in ['free_limit', 'slabs']}}
            })

            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_progress_percent(progress)
            
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()

    def perform_update_commodity_surcharge_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        data = self.data
        
        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })

        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']
        
        includes = {'id' : True}
        fcl_freight_rates = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= None, includes=includes)['list']
        fcl_freight_rates = list(fcl_freight_rates.dicts())

        total_count = len(fcl_freight_rates)
        count = 0

        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.select().where('bulk_operation_id' == self.id).limit(1).dicts().get():
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            update_fcl_freight_rate_data({
                'id': freight['id'],
                'performed_by_id': self.performed_by_id,
                'procured_by_id': procured_by_id,
                'sourced_by_id': sourced_by_id,
                'bulk_operation_id': self.id,
                'commodity_surcharge_price': data['price'],
                'commodity_surcharge_currency': data['currency']
            })

            progress = int((count * 100.0) / total_count)
            self.set_progress_percent(progress)
        self.progress = 100 if count == total_count else get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.save()


    def perform_update_weight_limit_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        total_affected_rates = 0
        data = self.data
        
        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })

        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']
        
        includes = {'id': True}
        fcl_freight_rates = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= None, includes=includes)['list']
        fcl_freight_rates = list(fcl_freight_rates.dicts())

        weight_limit = {key: value for key, value in data.items() if key in ['free_limit', 'slabs']}

        total_count = len(fcl_freight_rates)
        count = 0
        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.get_or_none(bulk_operation_id=self.id,object_id=freight["id"]):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            update_fcl_freight_rate_data({
                'id': freight["id"],
                'performed_by_id': self.performed_by_id,
                'procured_by_id': procured_by_id,
                'sourced_by_id': sourced_by_id,
                'bulk_operation_id': self.id,
                'weight_limit': weight_limit
            })

            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_progress_percent(progress)
       
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()  

    def perform_batch_extend_freight_rate_action(self, batch_query, count, total_count, total_affected_rates, sourced_by_id, procured_by_id, cogo_entity_id):
        data = self.data
        fcl_freight_rates = list(batch_query.dicts())

        total_count = len(fcl_freight_rates)
        count = 0
        
        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.get_or_none(bulk_operation_id=self.id,object_id=freight['id']):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue
                
            validities = [k for k in freight['validities'] if datetime.strptime(k['validity_end'], '%Y-%m-%d').date() >= datetime.now().date()]

            if not validities:
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            create_params = {key: value for key, value in freight.items() if key in ['origin_port_id', 'origin_main_port_id', 'destination_port_id', 'destination_main_port_id', 'container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'weight_limit', 'cogo_entity_id', 'rate_type', 'mode', 'sourced_by_id', 'procured_by_id']}

            create_params['performed_by_id'] = self.performed_by_id
            create_params['bulk_operation_id'] = self.id
            
            if not data.get("extend_for_flash_booking"):
                create_params['sourced_by_id'] = sourced_by_id
                create_params['procured_by_id'] = procured_by_id
                create_params['cogo_entity_id'] = cogo_entity_id

            for validity_object in validities:
                create_params['validity_start'] = validity_object['validity_start']
                create_params['validity_end'] = validity_object['validity_end']
                create_params['line_items'] = validity_object['line_items']
                create_params['schedule_type']: validity_object['schedule_type']
                create_params['payment_term']: validity_object['payment_term']

                line_item = [t for t in validity_object['line_items'] if t['code'] == data['line_item_code']][0]
                if not line_item:
                    continue

                validity_object['line_items'].remove(line_item)

                if data['markup_type'].lower() == 'percent':
                    markup = float(data['markup'] * line_item['price']) / 100 
                else:
                    markup = data['markup']

                if data['markup_type'].lower() == 'net':
                    markup = common.get_money_exchange_for_fcl({'from_currency':data['markup_currency'], 'to_currency':line_item['currency'], 'price':markup})['price']

                if data['markup_type'].lower() == 'absolute':
                    if data.get("extend_for_flash_booking"):
                        if not adjusted_price_for_flash_booking(line_item, markup):
                            continue
                    else:
                        line_item['price'] = markup
                else:
                    line_item['price'] = line_item['price'] + markup

                validity_object['line_items'].append(line_item)

                create_params['validity_start'] = max(datetime.strptime(validity_object["validity_start"], '%Y-%m-%d'), datetime.now())
                create_params['validity_end'] = datetime.strptime(validity_object["validity_end"], '%Y-%m-%d')
                
                if data.get("extend_for_flash_booking"):
                    freight_rate_object = create_params | ({ 'source': 'bulk_operation' })
                    id = create_fcl_freight_rate_data(freight_rate_object)
                    total_affected_rates += str(id) != str(freight["id"])
                    continue
                
                for commodity in data['commodities']:
                    freight_rate_object = create_params | ({ 'commodity': commodity, 'source': 'bulk_operation' })
                    
                    id = create_fcl_freight_rate_data(freight_rate_object)
                    total_affected_rates += str(id) != str(freight["id"])
                    
                for container_size in data['container_sizes']:
                    freight_rate_object = create_params | ({ 'container_size': container_size, 'source': 'bulk_operation' })
                    
                    id = create_fcl_freight_rate_data(freight_rate_object)
                    total_affected_rates += str(id) != str(freight["id"])
                    
                for container_type in data['container_types']:
                    freight_rate_object = create_params | ({ 'container_type': container_type, 'source': 'bulk_operation' })
                    
                    id = create_fcl_freight_rate_data(freight_rate_object)
                    total_affected_rates += str(id) != str(freight["id"])

            
        progress = int((count * 100.0) / total_count)
        self.set_progress_percent(progress)
        return count, total_affected_rates
    

    def perform_extend_freight_rate_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        total_affected_rates = 0
        data = self.data
        
        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })

        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']
        
        includes = {
            'id': True,
            'validities': True,
            'origin_port_id':True,
            'origin_main_port_id':True,
            'destination_port_id':True,
            'destination_main_port_id':True,
            'container_size':True,
            'container_type':True,
            'commodity':True,
            'shipping_line_id':True,
            'weight_limit': True,
            'service_provider_id':True,
            'cogo_entity_id': True,
            'rate_type': True,
            'sourced_by_id': True,
            'procured_by_id': True
        }
        
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_freight_rates_query = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= page_limit, includes=includes)['list']
        total_count = fcl_freight_rates_query.count()
        count = 0
        offset = 0
        
        while(offset < total_count):
            batch_query = fcl_freight_rates_query.offset(offset).limit(BATCH_SIZE)
            offset += BATCH_SIZE
            count, total_affected_rates = self.perform_batch_extend_freight_rate_action(batch_query, count , total_count, total_affected_rates, sourced_by_id, procured_by_id, cogo_entity_id)
        
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()  



    def perform_extend_freight_rate_to_icds_action(self, sourced_by_id, procured_by_id, cogo_entity_id=None):
        total_affected_rates = 0
        data = self.data
        
        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id' : cogo_entity_id })

        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']
        
        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']
        
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        fcl_freight_rate = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= page_limit)['list']
        fcl_freight_rate = list(fcl_freight_rate.dicts())
        if fcl_freight_rate:
            fcl_freight_rate = fcl_freight_rate[0]
            validities = [k for k in fcl_freight_rate["validities"] if datetime.strptime(k['validity_end'], '%Y-%m-%d').date() >= datetime.now().date()]
        else:
            validities = None

        if not validities or FclFreightRateAudit.get_or_none(bulk_operation_id=self.id,object_id=fcl_freight_rate['id']):
            self.progress = 100
            data['total_affected_rates'] = total_affected_rates
            self.data = data
            self.save()  
            return

        if data['origin_port_ids']:
            origin_port_ids = data['origin_port_ids']
        else:
            origin_port_ids = [fcl_freight_rate["origin_port_id"]]

        if data['destination_port_ids']:
            destination_port_ids = data['destination_port_ids']
        else:
            destination_port_ids = [fcl_freight_rate["destination_port_id"]]

        total_count = len(origin_port_ids) * len(destination_port_ids) * len(validities)
        count = 0

        create_params = {key: value for key, value in fcl_freight_rate.items() if key in ['container_size', 'container_type', 'commodity', 'shipping_line_id', 'service_provider_id', 'importer_exporter_id', 'cogo_entity_id', 'rate_type']}
        create_params['performed_by_id'] = self.performed_by_id
        create_params['sourced_by_id'] = sourced_by_id
        create_params['procured_by_id'] = procured_by_id
        create_params['cogo_entity_id'] = cogo_entity_id

        for validity_object in validities:
            create_params['validity_start'] = validity_object['validity_start']
            create_params['line_items'] = validity_object['line_items']
            validity_object["validity_start"]=datetime.strptime(validity_object['validity_start'], '%Y-%m-%d')
            validity_object["validity_end"]=datetime.strptime(validity_object['validity_end'], '%Y-%m-%d')
            create_params['validity_end'] = validity_object['validity_end']
            create_params['validity_start'] = max(validity_object["validity_start"], datetime.now())

            line_item = [t for t in validity_object['line_items'] if t['code'] == data['line_item_code']][0]

            if not line_item:
                count += (len(origin_port_ids) * len(destination_port_ids))
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)

            validity_object['line_items'].remove(line_item)

            if data['markup_type'].lower() == 'percent':
                markup = float(data['markup'] * line_item['price']) / 100 
            else:
                markup = data['markup']

            if data['markup_type'].lower() == 'net':
                markup = common.get_money_exchange_for_fcl({'from_currency': data['markup_currency'], 'to_currency': line_item['currency'], 'price': markup})['price']

            if data['markup_type'].lower() == 'absolute':
                line_item['price'] = markup
            else:  
                line_item['price'] = line_item['price'] + markup
            
            validity_object['line_items'].append(line_item)

            for origin_port_id in origin_port_ids:
                for destination_port_id in destination_port_ids:
                    count += 1
                    progress = int((count * 100.0) / total_count)
                    self.set_progress_percent(progress)

                    if (origin_port_id == fcl_freight_rate["origin_port_id"]) and (destination_port_id == fcl_freight_rate["destination_port_id"]):
                        continue

                    create_params['origin_port_id'] = origin_port_id
                    if origin_port_id != fcl_freight_rate["origin_port_id"]:
                        create_params['origin_main_port_id'] = fcl_freight_rate["origin_port_id"]

                    create_params['destination_port_id'] = destination_port_id
                    if destination_port_id != fcl_freight_rate["destination_port_id"]:
                        create_params['destination_main_port_id'] = fcl_freight_rate["destination_port_id"]
                    create_params['source'] = 'bulk_operation'
                    
                    create_fcl_freight_rate_data(create_params)
                    total_affected_rates+= 1
                    
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()


    def perform_add_local_conditions_action(self, sourced_by_id=None, procured_by_id=None, cogo_entity_id=None):
        data = self.data
        total_affected_rates = 0
        count = 0
        page_count = 1

        if not data['filters']:
            raise HTTPException(status_code=400, detail='filters cannot be empty')

        filters = data['filters']
        total_count = list_fcl_freight_rate_locals(filters= filters, get_count = True)['list']

        while True:
            batch_wise_local_rates = list_fcl_freight_rate_locals(filters= filters, return_query= True, page = page_count, page_limit = BATCH_SIZE)['list']
            page_count += 1

            if not batch_wise_local_rates:
                break

            for local in batch_wise_local_rates:
                count += 1

                if FclFreightRateAudit.get_or_none(bulk_operation_id = self.id,object_id = local['id']):
                    progress = int((count * 100.0) / total_count)
                    self.set_progress_percent(progress)
                    continue

                line_items = data['line_items']
                local_line_items = ((local.get('data') or {}).get('line_items',[]) or [])
                local_line_items_codes = []
                if local_line_items:
                    for local_line_item in local_line_items:
                        local_line_items_codes.append(local_line_item['code'])

                line_items_codes = []
                line_items_seperation = {}
                new_line_items = []
                for line_item in line_items:
                    code = line_item["code"]
                    if code in local_line_items_codes:
                        line_items_codes.append(code)
                        if not line_item["conditions"]:
                            key = "Default_{}".format(code)
                        else:
                            key = code
                        if key not in line_items_seperation:
                            line_items_seperation[key] = []
                        line_items_seperation[key].append(line_item)
                    else:
                        new_line_items.append({key: value for key, value in line_item.items() if key in ['code', 'unit', 'price', 'currency', 'conditions']})

                if  line_items_seperation:
                    completed_codes = []
                    for line_item in line_items:
                        local_line_items = local['data'].get('line_items')
                        code = line_item["code"]
                        if code not in completed_codes:

                            if "Default_{}".format(code) in line_items_seperation and code not in line_items_seperation:
                                matching_line_items = [t for t in local['data']['line_items'] if t['code'] == code]
                                local_line_items = [item for item in local_line_items if item not in matching_line_items]
                                for t in line_items_seperation[f"Default_{code}"]:
                                    local_line_items.append(t)
                                local['data']['line_items'] = local_line_items

                            if "Default_{}".format(code) in line_items_seperation and code in line_items_seperation:
                                matching_line_items = [t for t in local['data']['line_items'] if t['code'] == code]
                                local_line_items = [item for item in local_line_items if item not in matching_line_items]
                                for t in line_items_seperation[f"Default_{code}"]:
                                    local_line_items.append(t)
                                for t in line_items_seperation[code]:
                                    local_line_items.append(t)
                                local['data']['line_items'] = local_line_items

                            if not "Default_{}".format(code) in line_items_seperation and code in line_items_seperation:
                                matching_conditions_line_items = [t for t in local['data']['line_items'] if t['code'] == code and t.get('conditions')]
                                local_line_items = [item for item in local_line_items if item not in matching_conditions_line_items]
                                for t in line_items_seperation[code]:
                                    local_line_items.append(t)
                                local['data']['line_items'] = local_line_items

                            completed_codes.append(code)

                
                local['data'] = (local.get('data') or {})
                if 'line_items' not in local['data']:
                    local['data']['line_items'] = []

                if new_line_items:
                    for items in new_line_items:
                        local['data']['line_items'].append(items)

                try:
                    update_fcl_freight_rate_local({
                        'id': local['id'],
                        'performed_by_id': self.performed_by_id,
                        'sourced_by_id': local.get('sourced_by_id'),
                        'procured_by_id': local.get('procured_by_id'),
                        'bulk_operation_id': self.id,
                        'data': local['data']
                    })
                except :
                    pass

                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)

            total_affected_rates += count
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()


    def perform_delete_local_rate_line_item_action(self, sourced_by_id=None, procured_by_id=None, cogo_entity_id=None):
        data = self.data
        total_affected_rates = 0

        filters = (data['filters'] or {})
        
        page_limit = MAX_SERVICE_OBJECT_DATA_PAGE_LIMIT

        local_rates = list_fcl_freight_rate_locals(filters= filters, return_query= True, page_limit= page_limit)['list']
        total_count = len(local_rates)
        count = 0

        for local in local_rates:
            count += 1

            if FclFreightRateAudit.get_or_none(bulk_operation_id = self.id,object_id = local['id']):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            if not (local.get('data') or {}).get('line_items'):
                continue

            line_items = [t for t in local['data'].get('line_items',[]) if t.get('code') == data['line_item_code'] and t.get('conditions')]

            if not line_items:
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)

            local['data']['line_items'] = [t for t in local['data'].get('line_items',[]) if t not in line_items]

            update_fcl_freight_rate_local({
                'id': local['id'],
                'performed_by_id': self.performed_by_id,
                'sourced_by_id': local.get('sourced_by_id'),
                'procured_by_id': local.get('procured_by_id'),
                'bulk_operation_id': self.id,
                'data': local['data']
            })

            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_progress_percent(progress)
            
        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()

    def perform_batch_add_sailing_schedules_action(self, batch_query, count , total_count, total_affected_rates, sourced_by_id, procured_by_id):
        data = self.data
        
        validity_start = datetime.strptime(data['validity_start'], '%Y-%m-%d')
        validity_end = datetime.strptime(data['validity_end'], '%Y-%m-%d') 

        fcl_freight_rates = list(batch_query.dicts())

        for freight in fcl_freight_rates:
            count += 1

            if FclFreightRateAudit.get_or_none(bulk_operation_id=self.id, object_id=freight['id']):
                progress = int((count * 100.0) / total_count)
                self.set_progress_percent(progress)
                continue

            validities = [k for k in freight["validities"] if datetime.strptime(k['validity_end'], '%Y-%m-%d').date() >= datetime.now().date()]
            validity_id=None
            for validity_object in validities:
                validity_object['validity_start'] = datetime.strptime(validity_object['validity_start'], '%Y-%m-%d')
                validity_object['validity_end'] = datetime.strptime(validity_object['validity_end'], '%Y-%m-%d')
                
                if data['schedule_type'] == validity_object['schedule_type'] and validity_object['validity_start'] >= validity_start and  validity_object['validity_end'] <= validity_end:
                   validity_id = validity_object['id']
                   break
            
            if validity_id:
                data={
                    'validity_id':validity_id,
                    'rate_id':freight['id'],
                    'schedule_id':data['schedule_id'],
                    'schedule_type': data['schedule_type']
                }
                update_schedule_in_fcl_freight_rate(data)
            else:
                continue

            total_affected_rates += 1
            progress = int((count * 100.0) / total_count)
            self.set_progress_percent(progress)
        return count, total_affected_rates
            
            

    def perform_add_sailing_schedules_action(self, sourced_by_id=None, procured_by_id=None, cogo_entity_id=None):
        total_affected_rates = 0
        data = self.data

        filters = data['filters'] | ({ 'service_provider_id': self.service_provider_id, 'importer_exporter_present': False, 'partner_id': cogo_entity_id })

        if not filters['service_provider_id'] or filters['service_provider_id'] == 'None':
            del filters['service_provider_id']

        if not filters['partner_id'] or filters['partner_id'] == 'None':
            del filters['partner_id']

        includes = { 
                    'id': True,
                    'validities': True,
                }

        query = list_fcl_freight_rates(filters= filters, return_query= True, page_limit= None, includes=includes, sort_by="id")['list']
        total_count = query.count()
        count = 0
        offset = 0

        while(offset < total_count):
            batch_query = query.offset(offset).limit(BATCH_SIZE)
            offset += BATCH_SIZE
            count, total_affected_rates = self.perform_batch_add_sailing_schedules_action(batch_query, count , total_count, total_affected_rates, sourced_by_id, procured_by_id)

        data['total_affected_rates'] = total_affected_rates
        self.progress = 100 if count == total_count else  get_progress_percent(str(self.id), parse_numeric(self.progress) or 0)
        self.data = data
        self.save()   
        