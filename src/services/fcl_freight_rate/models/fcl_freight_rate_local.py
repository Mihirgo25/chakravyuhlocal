from peewee import *
from database.db_session import db
from playhouse.postgres_ext import *
import datetime
from configs.fcl_freight_rate_constants import TRADE_TYPES, CONTAINER_SIZES, CONTAINER_TYPES, LOCAL_CONTAINER_COMMODITY_MAPPINGS
from configs.global_constants import HAZ_CLASSES
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from configs.definitions import FCL_FREIGHT_LOCAL_CHARGES
from services.fcl_freight_rate.models.fcl_freight_rate_local_data import FclFreightRateLocalData
from services.fcl_freight_rate.models.fcl_freight_rate_free_day import FclFreightRateFreeDay
from micro_services.client import *
from database.rails_db import get_shipping_line
import concurrent.futures
from services.fcl_freight_rate.interaction.get_eligible_fcl_freight_rate_free_day import get_eligible_fcl_freight_rate_free_day

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = db
        only_save_dirty = True

class FclFreightRateLocal(BaseModel):
    commodity = CharField(index=True, null=True)
    container_size = CharField(index=True, null=True)
    container_type = CharField(index=True, null=True)
    containers_count = IntegerField(null=True)
    continent_id = UUIDField(null=True)
    country_id = UUIDField(null=True)
    created_at = DateTimeField( default=datetime.datetime.now)
    data = BinaryJSONField(constraints=[SQL("DEFAULT '{}'::jsonb")], null=True)
    demurrage_id = UUIDField(null=True)
    detention_id = UUIDField(null=True)
    id = UUIDField(constraints=[SQL("DEFAULT gen_random_uuid()")], primary_key=True)
    importer_exporters_count = IntegerField(null=True)
    is_demurrage_slabs_missing = BooleanField( null=True)
    is_detention_slabs_missing = BooleanField( null=True)
    is_line_items_error_messages_present = BooleanField( null=True)
    is_line_items_info_messages_present = BooleanField( null=True)
    is_plugin_slabs_missing = BooleanField(index=True, null=True)
    line_items = BinaryJSONField(null=True)
    line_items_error_messages = BinaryJSONField( null=True)
    line_items_info_messages = BinaryJSONField( null=True)
    location_ids = ArrayField(constraints=[SQL("DEFAULT '{}'::uuid[]")], field_class=UUIDField, null=True)
    main_port_id = UUIDField( null=True)
    main_port = BinaryJSONField(null=True)
    plugin_id = UUIDField( null=True)
    port_id = UUIDField(index=True, null=True)
    port = BinaryJSONField(null=True)
    procured_by_id = UUIDField( null=True)
    procured_by = BinaryJSONField(null=True)
    rate_not_available_entry = BooleanField(null=True)
    selected_suggested_rate_id = UUIDField(null=True)
    service_provider_id = UUIDField(index=True, null=True)
    service_provider = BinaryJSONField(null=True)
    shipping_line_id = UUIDField(index=True, null=True)
    shipping_line = BinaryJSONField(null=True)
    sourced_by_id = UUIDField( null=True)
    sourced_by = BinaryJSONField(null=True)
    trade_id = UUIDField(index=True, null=True)
    trade_type = CharField(index=True, null=True)
    updated_at = DateTimeField(index=True, default=datetime.datetime.now)

    def save(self, *args, **kwargs):
      self.updated_at = datetime.datetime.now()
      return super(FclFreightRateLocal, self).save(*args, **kwargs)


    class Meta:
        table_name = 'fcl_freight_rate_locals'

    def validate_main_port_id(self):
        # if self.port and self.port['is_icd']==False:
        #     if not self.main_port_id or self.main_port_id == self.port_id:
        #         return True
        #     return False
        if self.port and self.port['is_icd']==True:
            if self.main_port_id:
                if not self.main_port or self.main_port['is_icd'] == True:
                    return False
                return True
            else:
                return False
        return True


    def validate_trade_type(self):
        if self.trade_type not in TRADE_TYPES:
            return False
        return True

    def validate_container_size(self):
        if self.container_size not in CONTAINER_SIZES:
            return False
        return True

    def validate_container_type(self):
        if self.container_type not in CONTAINER_TYPES:
            return False
        return True

    def validate_commodity(self):
        if self.container_type and self.commodity not in LOCAL_CONTAINER_COMMODITY_MAPPINGS[self.container_type]:
            return False
        return True

    def validate_before_save(self):
        self.local_data_instance = FclFreightRateLocalData(self.data)

        if not self.validate_main_port_id():
            raise HTTPException(status_code=400, detail='main_port_id is not valid')

        if not self.validate_trade_type():
            raise HTTPException(status_code=400, detail='trade_type is not valid')

        if not self.validate_container_size():
            raise HTTPException(status_code=400, detail='container_size is not valid')

        if not self.validate_container_type():
            raise HTTPException(status_code=400, detail='container_type is not valid')

        if not self.validate_commodity():
            raise HTTPException(status_code=400, detail='commodity is not valid')

        if not self.local_data_instance.validate_duplicate_charge_codes():
            raise HTTPException(status_code=400, detail='duplicate line items present')

        invalid_charge_codes = []
        if not self.rate_not_available_entry:
            invalid_charge_codes = self.local_data_instance.validate_invalid_charge_codes(self.possible_charge_codes())

        if invalid_charge_codes:
            raise HTTPException(status_code=400, detail=f"{invalid_charge_codes} are invalid line items")

    def update_special_attributes(self, new_free_days: dict = {}, rate_sheet_validation: bool = False):
        if rate_sheet_validation:
            self.local_data_instance = FclFreightRateLocalData(self.data)
        self.update_line_item_messages()
        self.update_free_days_special_attributes(new_free_days)

    def update_line_item_messages(self):

        response = {}
        response = self.local_data_instance.get_line_item_messages(self.port, self.main_port, self.shipping_line_id, self.container_size, self.container_type, self.commodity,self.trade_type,self.possible_charge_codes())

        self.line_items_error_messages = response['line_items_error_messages'] if response['line_items_error_messages'] else None
        self.is_line_items_error_messages_present = response['is_line_items_error_messages_present']
        self.line_items_info_messages = response['line_items_info_messages'] if response['line_items_info_messages'] else None
        self.is_line_items_info_messages_present = response['is_line_items_info_messages_present']

    def update_free_days_special_attributes(self, new_free_days: dict = {}):
        self.is_detention_slabs_missing = len(new_free_days['detention']['slabs']) == 0 if new_free_days and new_free_days.get('detention') else True
        self.is_demurrage_slabs_missing = len(new_free_days['demurrage']['slabs']) == 0 if new_free_days and new_free_days.get('demurrage') else True
        self.is_plugin_slabs_missing = len(new_free_days['plugin']['slabs']) == 0 if new_free_days and new_free_days.get('plugin') else True

    def set_port(self):
        if self.port:
            return

        if not self.port_id:
            return

        location_ids = [str(self.port_id)]
        if self.main_port_id:
            location_ids.append(str(self.main_port_id))
        ports = maps.list_locations({'filters':{'id': location_ids}})['list']
        for port in ports:
            if str(port.get('id')) == str(self.port_id):
                self.country_id = port.get('country_id', None)
                self.trade_id = port.get('trade_id', None)
                self.continent_id = port.get('continent_id', None)
                self.location_ids = [uuid.UUID(str(x)) for x in [self.port_id, self.country_id, self.trade_id, self.continent_id] if x is not None]
                self.port = port
            elif self.main_port_id and str(port.get('id')) == str(self.main_port_id):
                self.main_port = port


    def set_shipping_line(self):
        if self.shipping_line or not self.shipping_line_id:
            return
        shipping_line = get_shipping_line(id=self.shipping_line_id)
        if len(shipping_line) != 0:
            shipping_line[0]['id']=str(shipping_line[0]['id'])
            self.shipping_line = {key:value for key,value in shipping_line[0].items() if key in ['id', 'business_name', 'short_name', 'logo_url']}

    def possible_charge_codes(self):
        self.set_port()
        self.set_shipping_line()

        # setting variables for conditions in charges.yml
        port = self.port
        main_port = self.main_port
        shipping_line_id = self.shipping_line_id
        container_size = self.container_size
        container_type = self.container_type
        commodity = self.commodity

        fcl_freight_local_charges_dict = FCL_FREIGHT_LOCAL_CHARGES

        charge_codes = {}
        for code, config in fcl_freight_local_charges_dict.items():
            if config.get('condition') is not None and eval(str(config['condition'])) and self.trade_type in config['trade_types']:
                charge_codes[code] = config

        return charge_codes

    def update_freight_objects(self):
        from services.fcl_freight_rate.models.fcl_freight_rate import FclFreightRate
        location_key = 'origin' if self.trade_type == 'export' else 'destination'
        if location_key == 'origin':
            kwargs = {
                'origin_local_id':self.id
            }
        else:
            kwargs = {
                'destination_local_id':self.id
            }
        commodity = self.commodity if self.commodity in HAZ_CLASSES else "general"
        t=FclFreightRate.update(**kwargs).where(
            FclFreightRate.container_size == self.container_size,
            FclFreightRate.container_type == self.container_type,
            FclFreightRate.shipping_line_id == self.shipping_line_id,
            FclFreightRate.service_provider_id == self.service_provider_id,
            (eval("FclFreightRate.{}_port_id".format(location_key)) == self.port_id),
            (eval("FclFreightRate.{}_main_port_id".format(location_key)) == self.main_port_id),
            FclFreightRate.commodity == commodity,
            (eval("FclFreightRate.{}_local_id".format(location_key)) == None)
            )
        t.execute()

    def detail(self):
        fcl_freight_local_charges_dict = FCL_FREIGHT_LOCAL_CHARGES

        free_day_ids = []

        detention_id = str(self.detention_id or '')
        demurrage_id = str(self.demurrage_id or '')
        plugin_id = str(self.plugin_id or '')

        if demurrage_id:
            free_day_ids.append(demurrage_id)
        if detention_id:
            free_day_ids.append(detention_id)
        if plugin_id:
            free_day_ids.append(plugin_id)

        free_days_charges = {}
        free_days_new = []  

        if len(free_day_ids):
            free_days_query = FclFreightRateFreeDay.select(
              FclFreightRateFreeDay.location_id,
              FclFreightRateFreeDay.id,
              FclFreightRateFreeDay.slabs,
              FclFreightRateFreeDay.free_days_type,
              FclFreightRateFreeDay.specificity_type,
              FclFreightRateFreeDay.is_slabs_missing,
              FclFreightRateFreeDay.free_limit
            ).where(FclFreightRateFreeDay.id << free_day_ids, (~FclFreightRateFreeDay.rate_not_available_entry | FclFreightRateFreeDay.rate_not_available_entry.is_null(True)))

            free_days_new = jsonable_encoder(list(free_days_query.dicts()))
        else:
            common_filters = {
                'location_id': self.location_ids,
                'trade_type': self.trade_type,
                'container_size': self.container_size,
                'container_type': self.container_type,
                'shipping_line_id': str(self.shipping_line_id),
                'service_provider_id': str(self.service_provider_id)
            }
            detention_filters = common_filters | {
                'free_days_type': 'detention'
            }
            demurrage_filters = common_filters | {
                'free_days_type': 'demurrage'
            }
            plugin_filters = common_filters | {
                'free_days_type': 'plugin'
            }

            with concurrent.futures.ThreadPoolExecutor(max_workers = 3) as executor:
                futures = [
                    executor.submit(get_eligible_fcl_freight_rate_free_day, detention_filters),
                    executor.submit(get_eligible_fcl_freight_rate_free_day, demurrage_filters),
                    executor.submit(get_eligible_fcl_freight_rate_free_day, plugin_filters)
                ]
                for i in range(0,len(futures)):
                    free_days_new.append(futures[i].result())

        for free_day_charge in free_days_new:
            if free_day_charge:
                free_days_charges[free_day_charge["id"]] = free_day_charge
                if free_day_charge['free_days_type']=='detention':
                    detention_id = free_day_charge['id']
                if free_day_charge['free_days_type']=='demurrage':
                    demurrage_id = free_day_charge['id']
                if free_day_charge['free_days_type']=='plugin':
                    plugin_id = free_day_charge['id']

        if detention_id and detention_id in free_days_charges:
            self.data["detention"] = free_days_charges[detention_id]

        if demurrage_id and demurrage_id in free_days_charges:
            self.data["demurrage"] = free_days_charges[demurrage_id]

        if plugin_id and plugin_id in free_days_charges:
            self.data["plugin"] = free_days_charges[plugin_id]

        detail = self.data | {
            'id': self.id,
            'line_items_error_messages': self.line_items_error_messages,
            'is_line_items_error_messages_present': self.is_line_items_error_messages_present,
            'line_items_info_messages': self.line_items_info_messages,
            'is_line_items_info_messages_present': self.is_line_items_info_messages_present,
            'is_detention_slabs_missing': self.is_detention_slabs_missing,
            'is_demurrage_slabs_missing': self.is_demurrage_slabs_missing,
            'is_plugin_slabs_missing': self.is_plugin_slabs_missing,
            'updated_at': self.updated_at,
            'procured_by_id': self.procured_by_id,
            'procured_by': self.procured_by,
            'sourced_by': self.sourced_by,
            'sourced_by_id': self.sourced_by_id
        }

        for item in detail.get('line_items',[]):
            line_item_name = fcl_freight_local_charges_dict[item['code']]['name'] if item['code'] in fcl_freight_local_charges_dict else item['code']
            item.update({'name': line_item_name})

        return detail
