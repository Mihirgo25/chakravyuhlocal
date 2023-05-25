from pydantic import BaseModel
from datetime import datetime, timedelta,date
from peewee import *
from typing import List
from dateutil.relativedelta import relativedelta

class WeightSlab(BaseModel):
    lower_limit: float
    upper_limit: float
    tariff_price: float
    currency: str
    unit:str ='per_kg'

class DeleteAirFreightRate(BaseModel):
    id:str
    validity_id:str
    performed_by_id:str =None
    performed_by_type:str =None
    bulk_operation_id:str = None
    sourced_by_id: str = None
    procured_by_id: str = None

class UpdateAirFreightRate(BaseModel):
    id:str
    validity_id:str=None
    validity_start:datetime=None
    validity_end:datetime=None
    currency:str=None
    min_price:float=None
    performed_by_id:str=None
    bulk_operation_id:str=None
    weight_slabs: list[WeightSlab]=None
    length:float=None
    breadth:float=None
    height:float=None
    maximum_weight:float=None
    procured_by_id:str=None
    sourced_by_id:str=None
    available_volume:float=None
    available_gross_weight:float=None

class GetAirFreightRate(BaseModel):
    origin_airport_id:str
    destination_airport_id:str
    commodity:str
    commodity_type:str=None
    commodity_sub_type:str =None
    airline_id:str
    operation_type:str
    service_provider_id:str=None
    shipment_type:str ='box'
    stacking_type:str = 'stackable'
    validity_start:datetime =datetime.now()
    validity_end:datetime =datetime.now()
    weight:float =None
    cargo_readiness_date:date
    price_type:str=None
    cogo_entity_id:str=None






