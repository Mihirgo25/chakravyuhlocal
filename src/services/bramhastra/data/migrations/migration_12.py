from services.locations.models.planet import Planet
import random
import uuid
from services.operators.models.operator import Operator
from datetime import datetime,timedelta,date
from fastapi.encoders import jsonable_encoder
from joblib import delayed, Parallel, cpu_count
from clickhouse_driver import Client
from enum import Enum
import time

from peewee import (Model,BigIntegerField,UUIDField,IntegerField,FloatField,DateField,BooleanField)

from playhouse.postgres_ext import (DateTimeTZField,BigAutoField,TextField,CharField,ArrayField)


from datetime import datetime
import sys
from playhouse.pool import PooledPostgresqlExtDatabase 
DEFAULT_UUID = "00000000-0000-0000-0000-000000000000"
GLOBAL_MIN = -1000000000000000  # 10e-15
DEFAULT_ENUM = 'empty'

db = PooledPostgresqlExtDatabase(
    "ocean_rms_dev",
    user="nirvana1",
    password="lVHp1GUcwCpqfS0MRKG3",
    host="localhost",
    port=6432,
    autorollback=True,
    max_connections=200,
)

class BaseModel(Model):     
    class Meta: 
        database = db

class Bramhastra(Enum):
    pass


class FclModes(Bramhastra):
    rate_extension = "rate_extension"
    manual = "manual"
    rate_sheet = "rate_sheet"
    predicted = "predicted"
    cluster_extension = "cluster_extension"
    disliked_rate = "disliked_rate"
    flash_booking = "flash_booking"
    rms_upload = "rms_upload"
    missing_rate = "missing_rate"
    spot_negotation = "spot_negotation"
    cogolens = "cogolens"

class ImportTypes(Bramhastra):
    parquet = "parquet"
    csv = "csv"
    postgres = "postgres"

class FclFreightAction(BaseModel):
    id = BigAutoField()
    fcl_freight_rate_statistic_id = BigIntegerField(index=True, null=True)
    origin_port_id = UUIDField(index=True, default=DEFAULT_UUID)
    destination_port_id = UUIDField(index=True, default=DEFAULT_UUID)
    origin_main_port_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_main_port_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    origin_region_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_region_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    origin_country_id = UUIDField(index=True, default=DEFAULT_UUID)
    destination_country_id = UUIDField(index=True, default=DEFAULT_UUID)
    origin_continent_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_continent_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    origin_trade_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    destination_trade_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    commodity = TextField(null=True, index=True)
    container_size = TextField(null=True, index=True)
    container_type = TextField(null=True, index=True)
    service_provider_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    rate_id = UUIDField(index=True, default=DEFAULT_UUID)
    validity_id = UUIDField(index=True, default=DEFAULT_UUID)
    bas_price = FloatField(default=0, null=True)
    bas_standard_price = FloatField(default=0, null=True)
    standard_price = FloatField(default=0, null=True)
    price = FloatField(default=0, null=True)
    currency = CharField(max_length=3, null=True)
    market_price = FloatField(default=0, null=True)
    bas_currency = CharField(max_length=3, null=True)
    mode = CharField(index=True, null=True)
    parent_mode = CharField(index=True, null=True)
    parent_rate_mode = CharField(index=True, null=True)
    source = CharField(index=True, default=FclModes.manual.value, null=True)
    source_id = UUIDField(index=True, default=DEFAULT_UUID, null=True)
    sourced_by_id = UUIDField(index=True, default=DEFAULT_UUID, null=True)
    procured_by_id = UUIDField(index=True, default=DEFAULT_UUID, null=True)
    performed_by_id = UUIDField(index=True, default=DEFAULT_UUID, null=True)
    rate_type = CharField(null=True)
    validity_start = DateField(null=True)
    validity_end = DateField(null=True)
    shipping_line_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    importer_exporter_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    spot_search_id = UUIDField(index=True, default=DEFAULT_UUID)
    spot_search_fcl_freight_service_id = UUIDField(null=True, default=DEFAULT_UUID)
    spot_search = IntegerField(default=0, null=True)
    checkout_source = CharField(null=True)
    checkout_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    checkout_fcl_freight_service_id = UUIDField(null=True, default=DEFAULT_UUID)
    checkout = IntegerField(default=0, null=True)
    checkout_created_at = DateTimeTZField(null=True)
    shipment = IntegerField(default=0, null=True)
    shipment_id = UUIDField(null=True, index=True, default=DEFAULT_UUID)
    shipment_source = CharField(null=True)
    containers_count = IntegerField(null=True, default=0)
    cargo_weight_per_container = FloatField(null=True, default=0)
    shipment_state = CharField(null=True, default=DEFAULT_ENUM)
    shipment_service_id = UUIDField(null=True, default=DEFAULT_UUID)
    shipment_cancellation_reason = TextField(null=True, index=True)
    shipment_source_id = UUIDField(null=True, default=DEFAULT_UUID)
    shipment_created_at = DateTimeTZField(null=True)
    shipment_updated_at = DateTimeTZField(null=True)
    shipment_service_state = CharField(null=True, default=DEFAULT_ENUM)
    shipment_service_is_active = CharField(null=True)
    shipment_service_created_at = DateTimeTZField(null=True)
    shipment_service_updated_at = DateTimeTZField(null=True)
    shipment_service_cancellation_reason = TextField(null=True)
    feedback_type = CharField(null=True, default=DEFAULT_ENUM)
    feedback_state = CharField(null=True, default=DEFAULT_ENUM)
    feedback_ids = ArrayField(UUIDField, null=True)
    rate_request_state = CharField(null=True, default=DEFAULT_ENUM)
    rate_requested_ids = ArrayField(UUIDField, null=True)
    selected_bas_standard_price = FloatField(default=0, null=True)
    bas_standard_price_accuracy = FloatField(default=0, null=True) 
    bas_standard_price_diff_from_selected_rate = FloatField(default=0, null=True)
    selected_fcl_freight_rate_statistic_id = BigIntegerField(default=0, null=True)
    selected_rate_id = UUIDField(index=True, null=True, default=DEFAULT_UUID)
    selected_validity_id = UUIDField(index=True, null=True, default=DEFAULT_UUID)
    selected_type = CharField(index=True, null=True)
    revenue_desk_state = CharField(null=True, default=DEFAULT_ENUM)
    given_priority = IntegerField(default=0, null=True)
    rate_created_at = DateTimeTZField(index=True, null=True)
    rate_updated_at = DateTimeTZField(index=True, null=True)
    validity_created_at = DateTimeTZField(index=True, null=True)
    validity_updated_at = DateTimeTZField(index=True, null=True)
    created_at = DateTimeTZField(index=True, default=datetime.utcnow())
    updated_at = DateTimeTZField(index=True, default=datetime.utcnow())
    operation_created_at = DateTimeTZField(default=datetime.utcnow())
    operation_updated_at = DateTimeTZField(default=datetime.utcnow(), index=True)

    def save(self, *args, **kwargs):
        self.operation_updated_at = datetime.utcnow()
        return super(FclFreightAction, self).save(*args, **kwargs)
    
    @classmethod
    def update(cls, *args, **kwargs):
        kwargs['updated_at'] = datetime.now()
        return super().update(*args, **kwargs)

    def refresh(self):
        return type(self).get(self._pk_expr())

    class Meta:
        table_name = "fcl_freight_actions"

        CLICK_KEYS = [
            "origin_continent_id",
            "parent_mode",
            "origin_country_id",
            "container_size",
            "rate_id",
            "id",
        ]

    IMPORT_TYPE = ImportTypes.csv.value

def json_encoder_for_clickhouse(data):
    return jsonable_encoder(data, custom_encoder={datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")})


def get_start_and_end_dates():
    from datetime import datetime, timedelta
    def generate_date_range(start_date, end_date, interval_days):
        date_range = []
        current_date = start_date
        while current_date < end_date:
            next_date = current_date + timedelta(days=interval_days)
            date_range.append({
                'validity_start': current_date,
                'validity_end': next_date
            })
            current_date = next_date
        return date_range

    start_date = datetime(2023, 8, 8)
    end_date = datetime(2023, 11, 8)
    interval_days = 15

    return generate_date_range(start_date, end_date, interval_days)


def get_random_uuid():
    return uuid.uuid4()

def get_price():
    return float(random.randrange(1000, 2000))

def get_market_price():
    return (random.randrange(1000,3000)) + 0.032456

def get_mode():
    NEEDED_MODES = ["rate_extension","manual","rate_sheet","predicted","cluster_extension","disliked_rate","flash_booking","rms_upload","missing_rate","spot_negotation","cogolens"]
    return NEEDED_MODES[random.randrange(0,len(NEEDED_MODES))]

def get_parent_mode():
    NEEDED_MODES = ["rate_extension", "cluster_extension", "predicted", "supply"]
    return NEEDED_MODES[random.randrange(0,len(NEEDED_MODES))]

def get_parent_rate_mode():
    NEEDED_MODES = ["none","predicted", "disliked"]
    return NEEDED_MODES[random.randrange(0,len(NEEDED_MODES))]

def get_small_count():
    return random.randrange(1, 10)

def get_zero_or_one():
    return random.randrange(0, 2)

def get_likes_count():
    return random.randrange(1, 100)

def get_percentage():
    return float(random.randrange(-50,100))

def get_shipping_line(arr):
    return arr[random.randrange(0,len(arr))]

class FeedbackType(Bramhastra):
    empty = 0
    disliked = 1
    liked = 2

class FeedbackState(Bramhastra):
    empty = 0
    created = 1
    closed = 2
    rate_added = 3

class RateRequestState(Bramhastra):
    empty = 0
    created = 1
    closed = 2
    rate_added = 3

class RevenueDeskState(Bramhastra):
    empty = 0
    visited = 1
    selected_for_preference = 2
    selected_for_booking = 3

class ShipmentState(Bramhastra):
    empty = 0
    shipment_received = 1
    confirmed_by_importer_exporter = 2
    in_progress = 3
    cancelled = 4
    aborted = 5
    completed = 6

class ShipmentServiceState(Bramhastra):
    empty = 0
    init = 1
    containers_gated_out = 2
    containers_gated_in = 3
    cancelled = 4
    awaiting_service_provider_confirmation = 5
    confirmed_by_service_provider = 6
    vessel_arrived = 7
    vessel_departed = 8
    completed = 9
    aborted = 10

def random_feedback_type():
    return random.randrange(0, 3)

def random_feedback_state():
    return random.randrange(0, 4)

def random_request_state():
    return random.randrange(1, 4)

def random_revenue_desk_state():
    return random.randrange(0, 4)

def random_shipment_state():
    return random.randrange(1, 7)

def get_from_enum(enum, idx):
    values = [e.name for e in enum]
    return values[idx]

def add_correct_data(arr, row):

    if get_small_count() < 9:
        return

    revenue_desk_state = random_revenue_desk_state()

    if revenue_desk_state>0:
        row['checkout_source']=''
        row['checkout_id']=get_random_uuid()
        row['checkout_fcl_freight_service_id']=get_random_uuid()
        row['checkout']=1
        row['checkout_created_at']=row['created_at']
        
        for i in range(1,revenue_desk_state+1):
            row['revenue_desk_state']=get_from_enum(RevenueDeskState,i)
            arr.append(row)

        for i in range(1,random_shipment_state()+1):
            row['shipment_state'] = get_from_enum(ShipmentState,i)
            arr.append(row)
        
    else:
        feedback_type = random_feedback_type()
        if feedback_type>0:
            row['feedback_type'] = get_from_enum(FeedbackType,feedback_type)
            row['feedback_ids'] = [get_random_uuid()]
            if feedback_type == 2:
                row['feedback_state'] = get_from_enum(FeedbackState,1)
                arr.append(row)
            else:
                for i in range(1,random_feedback_state()+1):
                    row['feedback_state'] = get_from_enum(FeedbackState,i)
                    arr.append(row)
        else:
            row['rate_requested_ids'] = [get_random_uuid()]
            for i in range(1,random_request_state()+1):
                row['rate_request_state'] = get_from_enum(RateRequestState,i)
                arr.append(row)

def handle_update_rates(arr):
    for indx, row in enumerate(arr):
        if(indx%100==0):
            print(indx,'/',len(arr))
        spot_search_id = row['spot_search_id']
        rate_id = row['rate_id']

        action = FclFreightAction.select().where(FclFreightAction.spot_search_id==spot_search_id, FclFreightAction.rate_id==rate_id).first()

        if action:
            for key, value in row.items():
                setattr(action, key, value)
            action.save()
        else:
            print(' ❌ ')


def main():
    shipping_lines = jsonable_encoder([i['id'] for i in list(Operator.select(Operator.id).where(Operator.short_name.in_(['Maersk','MAERSK','ALX','Aiyer Shipping','Ben Line-Uafl'])).limit(20).dicts())])
    container_commodity_mapping = {'standard': ['white_goods','pta']}
    container_sizes = ['40','20']
    count = 0
    rates=[]
    updated_rates = []

    countries = jsonable_encoder(list(Planet.select(Planet.id).where(Planet.type == 'country', Planet.status=='active').limit(32).dicts()))
    countries = [value for item in countries for key, value in item.items() ]

    # if '541d1232-58ce-4d64-83d6-556a42209eb7' not in countries:
    #     countries.append('541d1232-58ce-4d64-83d6-556a42209eb7')

    # for o_idx, origin_country_id in enumerate(countries):
    for o_idx, origin_country_id in enumerate(['541d1232-58ce-4d64-83d6-556a42209eb7']):
        for d_idx, destination_country_id in enumerate(countries):
            print('\n', o_idx, ' 🟢 ', d_idx, '\n')

            # if get_small_count() < 8:
            #     continue
    
            if origin_country_id == '541d1232-58ce-4d64-83d6-556a42209eb7':
                origins = jsonable_encoder(list(Planet.select(Planet.id,Planet.country_id,Planet.region_id,Planet.continent_id,Planet.trade_id).where(Planet.type == 'seaport', Planet.port_code.in_(['INMUN','INNSA']) ).dicts()))
            else:
                origins = jsonable_encoder(list(Planet.select(Planet.id,Planet.country_id,Planet.region_id,Planet.continent_id,Planet.trade_id).where(Planet.type == 'seaport', Planet.status == 'active', Planet.country_id == origin_country_id).limit(2).dicts()))
            destinations = jsonable_encoder(list(Planet.select(Planet.id,Planet.country_id,Planet.region_id,Planet.continent_id,Planet.trade_id).where(Planet.type == 'seaport', Planet.status == 'active', Planet.country_id == destination_country_id).limit(2).dicts()))

            for origin in origins:
                for destination in destinations:

                    if origin_country_id == destination_country_id:
                        continue

                    for ck in container_commodity_mapping.keys():
                        for commodity in container_commodity_mapping[ck]:  
                            for container_size in container_sizes:
                                for date in get_start_and_end_dates():
                                    
                                    action_row = json_encoder_for_clickhouse({
                                        'id': count+1,
                                        'fcl_freight_rate_statistic_id': count+2,
                                        'origin_port_id': origin['id'],
                                        'destination_port_id':destination['id'],
                                        'origin_main_port_id': origin['id'],
                                        'destination_main_port_id': destination['id'],
                                        'origin_region_id': "00000000-0000-0000-0000-000000000000",
                                        'destination_region_id': "00000000-0000-0000-0000-000000000000",
                                        'origin_country_id': origin['country_id'],
                                        'destination_country_id': destination['country_id'],
                                        'origin_continent_id': origin['continent_id'],
                                        'destination_continent_id': destination['continent_id'],
                                        'origin_trade_id': origin['trade_id'],
                                        'destination_trade_id': destination['trade_id'],

                                        'commodity': commodity,
                                        'container_size': container_size,
                                        'container_type': ck,
                                        'service_provider_id': '72ee9958-8d53-4e48-8b7f-5cbbc43948be',
                                        'rate_id':get_random_uuid(),
                                        'validity_id': get_random_uuid(),

                                        'bas_price': get_price(),
                                        'bas_standard_price': get_price(),
                                        'standard_price': get_price(),
                                        'price': get_price(),
                                        'currency': 'USD',
                                        'market_price': get_market_price(),
                                        'bas_currency': 'USD',

                                        'mode': get_mode(),
                                        'parent_mode': get_parent_mode(),
                                        'parent_rate_mode': get_parent_rate_mode(),
                                        'source': 'rate_sheet',
                                        'source_id': get_random_uuid(),             
                                        'sourced_by_id': get_random_uuid(),
                                        'procured_by_id': get_random_uuid(),
                                        'performed_by_id': get_random_uuid(),                     
                                        'rate_type': 'market_place',
                                        'validity_start': date['validity_start'],
                                        'validity_end': date['validity_end'],
                                        'shipping_line_id': get_shipping_line(shipping_lines),
                                        'importer_exporter_id': get_random_uuid(),
                                        'spot_search_id': get_random_uuid(),
                                        'spot_search_fcl_freight_service_id': get_random_uuid(),
                                        'spot_search': get_small_count(), # why ?

                                        'checkout_source': '',
                                        'checkout_id': None,
                                        'checkout_fcl_freight_service_id': None,
                                        'checkout': 0, # why ?
                                        'checkout_created_at': None,

                                        'shipment': get_zero_or_one(),
                                        'shipment_id': get_random_uuid(),
                                        'shipment_source': '',
                                        'containers_count': get_small_count(),
                                        'cargo_weight_per_container': get_small_count()+get_small_count(),
                                        'shipment_state': 'empty',
                                        'shipment_service_id': get_random_uuid(),
                                        'shipment_cancellation_reason': '',
                                        'shipment_source_id': get_random_uuid(),
                                        'shipment_created_at': date['validity_start'],
                                        'shipment_updated_at': date['validity_start'],
                                        'shipment_service_state': 'empty',
                                        'shipment_service_is_active': get_zero_or_one(),
                                        'shipment_service_created_at': date['validity_start'],
                                        'shipment_service_updated_at': date['validity_start'],
                                        'shipment_service_cancellation_reason': '',

                                        'feedback_type': 'empty',
                                        'feedback_state': 'empty',
                                        'feedback_ids': None,

                                        'rate_request_state': 'empty',
                                        'rate_requested_ids': None,

                                        'selected_bas_standard_price': get_price(),
                                        'bas_standard_price_accuracy': get_percentage(),
                                        'bas_standard_price_diff_from_selected_rate': get_price(),
                                        'selected_fcl_freight_rate_statistic_id': None,
                                        'selected_rate_id': None,
                                        'selected_validity_id': None,
                                        'selected_type': '',
                                        'revenue_desk_state': 'empty',
                                        'given_priority': None,

                                        'rate_created_at': date['validity_start'],
                                        'rate_updated_at': date['validity_start'],
                                        'validity_created_at': date['validity_start'],
                                        'validity_updated_at': date['validity_start'],
                                        'created_at': date['validity_start'],
                                        'updated_at': date['validity_start'],
                                        'operation_created_at': date['validity_start'],
                                        'operation_updated_at': date['validity_start']
                                    })
                
                                    count+=1
                                    rates.append(action_row)
                                    
                                    add_correct_data(updated_rates,action_row)

                                    if len(rates) >= 1000:
                                        print('--> ',count)       
                                        print('INSERTING DATA ...')
                                        FclFreightAction.insert_many(rates).execute()
                                        rates = []
                                        
                                        # time.sleep(3)
                                        print('UPDATING RATES ...')
                                        handle_update_rates(updated_rates)
                                        updated_rates=[]
                                        print()

    print('✅',count)       
    print('INSERTING DATA ...')
    FclFreightAction.insert_many(rates).execute()
    rates = []

    time.sleep(3)
    print('UPDATING RATES ...')
    handle_update_rates(updated_rates)
    updated_rates=[]

main()