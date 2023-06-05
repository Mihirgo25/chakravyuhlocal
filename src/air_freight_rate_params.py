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

class Slab(BaseModel):
    lower_limit: float
    upper_limit: float
    price: float
    currency: str

class Item(BaseModel):
    packing_type:str=None
    handling_type:str=None
    packages_count:int=None
    package_weight:float=None
    height:float=None
    length:float=None
    width:float=None

class LineItem(BaseModel):
  code: str
  unit: str
  price: float
  currency: str
  min_price: float  
  remarks: list[str] = None

class TaskLineItem(BaseModel):
    location_id: str = None
    code: str
    unit: str
    price: float
    currency: str
    market_price: float = None 
    remarks: list[str] = None
    slabs: list[Slab] = None
class LineItemLocal(BaseModel):
    code: str
    unit: str
    min_price: float 
    price: float
    currency: str
    remarks: list[str] = None
class LocalData(BaseModel):
    line_items: list[TaskLineItem]=None

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
    performed_by_type:str =None
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
    cargo_readiness_date:datetime
    price_type:str=None
    cogo_entity_id:str=None
    trade_type:str=None
    volume:float =None
    predicted_rates_required:bool=False

class GetAirFreightRateSurcharge(BaseModel):

    origin_airport_id:str=None
    destination_airport_id:str=None
    commodity:str=None
    airline_id:str=None
    operation_type:str=None
    service_provider_id:str=None

class CreateAirFreightRateSurcharge(BaseModel):
    origin_airport_id:str
    destination_airport_id:str
    commodity:str
    commodity_type:str
    airline_id:str
    operation_type:str
    service_provider_id:str
    performed_by_id:str
    procured_by_id:str
    sourced_by_id:str
    bulk_operation_id:str=None
    rate_sheet_id:str=None
    line_items: list[LineItem]



class CreateAirFreightRateLocal(BaseModel):
    airport_id:str
    airline_id:str=None
    trade_type:str=None
    commodity:str=None
    commodity_type:str=None
    service_provider_id:str=None
    performed_by_id:str=None
    procured_by_id:str=None
    sourced_by_id:str=None
    bulk_operation_id:str=None
    rate_sheet_id:str=None
    rate_type:str='general'
    line_items: list[LineItemLocal]=None
    slabs:list[Slab]=None


class UpdateAirFreightRateSurcharge(BaseModel):
    id: str
    performed_by_id: str
    procured_by_id: str=None
    sourced_by_id: str=None
    line_items: list[LineItem]

class CreateAirFreightRateTask(BaseModel):
    service: str=None
    airport_id: str=None
    commodity: str=None
    commodity_type:str=None
    trade_type: str=None
    airline_id: str=None
    logistics_service_type:str=None
    source: str=None
    task_type: str=None
    shipment_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    rate: LocalData = None

class ListSlab(BaseModel):
    lower_limit:int
    upper_limit:int
    price:float
    currency:str

class CreateAirFreightRateLocal(BaseModel):
    airport_id:str
    airline_id:str=None
    trade_type:str=None
    commodity:str=None
    commodity_type:str=None
    service_provider_id:str=None
    performed_by_id:str=None
    procured_by_id:str=None
    sourced_by_id:str=None
    bulk_operation_id:str=None
    rate_sheet_id:str=None
    rate_type:str='general'
    line_items: list[LineItemLocal]=None
    slabs:list[Slab]=None
class LocalSlabs(BaseModel):
    lower_limit:int
    upper_limit:int
    price:float
    currency:str

class LineItemsLocal(BaseModel):
    code:str
    unit:str
    price:float
    min_price:float
    currency:str
    remarks:list[str]=None
    slabs:list[LocalSlabs]=None
    
class UpdateFrieghtRateLocal(BaseModel):
    id:str
    performed_by_id:str=None
    sourced_by_id:str=None
    procured_by_id:str=None
    bulk_operation_id:str=None
    line_items:list[LineItemsLocal]=None
    
class CreateAirFrieghtRateNotAvailable(BaseModel):
    origin_airport_id:str
    origin_country_id:str
    origin_trade_id:str
    destination_airport_id:str
    destination_country_id:str
    destination_trade_id:str
    commodity:str

class UpdateAirFreightRateSurcharge(BaseModel):
    id: str
    performed_by_id: str
    procured_by_id: str=None
    sourced_by_id: str=None
    line_items: list[LineItem]

class CreateAirFreightRateTask(BaseModel):
    service: str=None
    airport_id: str=None
    commodity: str=None
    commodity_type:str=None
    trade_type: str=None
    airline_id: str=None
    logistics_service_type:str=None
    source: str=None
    task_type: str=None
    shipment_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    rate: LocalData = None

class UpdateAirFreightRateTask(BaseModel):
  id: str
  performed_by_id: str=None
  performed_by_type: str=None
  rate: LocalData = None
  status: str = None
  closing_remarks: str = None

class CreateAirFreightRateFeedbacks(BaseModel):
  source: str
  source_id: str
  performed_by_id: str = None
  performed_by_org_id: str
  performed_by_type: str = None
  rate_id: str
  validity_id: str
  likes_count: int
  dislikes_count: int
  feedbacks: list[str] = []
  remarks: list[str] = []
  preferred_freight_rate: float = None
  preferred_freight_rate_currency: str = None
  preferred_airline_ids: list[str] = []
  feedback_type: str
  booking_params: dict = {}
  cogo_entity_id: str = None
  origin_port_id: str = None
  origin_trade_id: str = None
  origin_country_id: str = None
  origin_continent_id: str = None
  destination_port_id: str = None
  destination_continent_id: str = None
  destination_trade_id: str = None
  destination_country_id: str = None
  commodity: str = None
  container_size: str = None
  container_type: str = None
  service_provider_id: str = None
  attachment_file_urls: List[str] =[]
  commodity_description:str=None

class CreateAirFreightRateRequest(BaseModel):
  source: str
  source_id: str
  cogo_entity_id: str
  performed_by_id: str = None
  performed_by_org_id: str
  performed_by_type: str = None
  preferred_freight_rate: float = None
  preferred_freight_rate_currency: str = None
  preferred_detention_free_days: int = None
  preferred_storage_free_days: int = None
  cargo_readiness_date: datetime = None
  preferred_airline_ids: list[str] = []
  remarks: list[str] = []
  booking_params: dict = {}
  weight:float=None
  volume:float=None
  inco_term: str
  commodity: str = None
  commodity_type:str=None
  commodity_sub_type:str=None
  cargo_stacking_type:str=None
  packages_count:int=None
  trade_type:str=None
  airline_id:str=None
  service_provider_id:str=None
  price_type:str=None
  operation_type:str=None
  destination_continent_id: str = None
  destination_country_id: str = None
  destination_airport_id: str
  destination_trade_id: str = None
  origin_continent_id: str = None
  origin_country_id: str = None
  origin_airport_id: str
  origin_trade_id: str = None
  packages:list[Item]=None

class WarehouseLineItems(BaseModel):
    code:str
    unit:str
    min_price:float
    currency:str
    remarks:list=[]
    slabs:list[Slab]=None
class CreateAirFreightWarehouseRates(BaseModel):
    airport_id:str
    trade_type:str
    commodity:str
    service_provider_id:str
    performed_by_id:str
    procured_by_id:str
    sourced_by_id:str
    bulk_operation_id:str=None
    rate_sheet_id:str=None
    lineitems:list[WarehouseLineItems]=None

class UpdateAirFreightStorageRates(BaseModel):
    id :str =None
    performed_by_id:str=None
    bulk_operation_id:str=None
    free_limit:int=None
    slabs:list[Slab]=[]