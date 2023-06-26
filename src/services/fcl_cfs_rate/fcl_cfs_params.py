from pydantic import BaseModel
from datetime import datetime
from peewee import *
from typing import List

class Slab(BaseModel):
  lower_limit: float
  upper_limit: float
  price: float
  currency: str

class StandardLineItem(BaseModel):
  code: str
  unit: str
  price: float
  currency: str
  remarks: list[str] = []
  slabs: list[Slab] = []

class FreeDaysType(BaseModel):
  free_days_type:str
  free_limit:int
  slabs: list[Slab]

class CreateFclCfsRate(BaseModel):
  rate_sheet_id:str = None
  location_id: str
  trade_type: str
  container_size: str
  container_type: str
  commodity: str = None
  service_provider_id: str
  sourced_by_id: str
  procured_by_id: str
  cargo_handling_type: str
  importer_exporter_id: str = None
  line_items: list[StandardLineItem]
  free_days: list[FreeDaysType]
  performed_by_id: str = None
  performed_by_type: str = None
  rate_type: str = 'market_place'
  mode: str = None

class CreateFclCfsRateRequest(BaseModel):
    source: str 
    source_id:str 
    performed_by_id : str
    performed_by_org_id: str
    performed_by_type: str
    preferred_rate: float = None
    preferred_rate_currency: str= None
    cargo_readiness_date: datetime = None
    remarks:list[str] =[]
    booking_params : dict = {}
    container_size: str = None
    commodity: str = None
    country_id: str = None
    port_id: str = None
    trade_type: str = None

class DeleteFclCfsRate(BaseModel):
    id: str
    performed_by_id: str = None
    performed_by_type: str = None
    bulk_operation_id: str = None
    sourced_by_id: str = None
    procured_by_id: str = None
    rate_type: str = 'market_place'

class DeleteFclCfsRateRequest(BaseModel):
  fcl_cfs_rate_request_ids: List[str]
  closing_remarks: List[str] = []
  performed_by_id: str = None
  performed_by_type: str = None


class CreateFclCfsRateNotAvailable(BaseModel):
  location_id: str
  country_id: str = None
  trade_type: str
  container_size: str
  container_type: str
  commodity: str = None
  performed_by_type: str
  performed_by_id: str

class UpdateFclCfsRate(BaseModel):
    id: str 
    performed_by_id: str = None
    sourced_by_id: str 
    procured_by_id: str 
    bulk_operation_id: str = None
    line_items: list[StandardLineItem] = []
    free_limit: int = None
    performed_by_type: str = None
    rate_type: str = 'market_place'
    
class Filters(BaseModel):
  filters: dict = {}

class AddMarkUp(BaseModel):
  filters : dict = {}
  markup : float
  line_item_code : str
  markup_type : str
  markup_currency : str = None

  
class CreateFclCfsRateBulkOperation(BaseModel):
  performed_by_id: str = None
  service_provider_id: str 
  sourced_by_id: str 
  procured_by_id: str 
  performed_by_type: str = None
  delete_rate: Filters = None
  add_markup: AddMarkUp = None

class UpdateFclCfsRatePlatformPrice(BaseModel):
  location_id: str
  container_size: str 
  container_type: str 
  commodity: str = None
  trade_type:str
  performed_by_id: str
  performed_by_type: str
  importer_exporter_id: str = None
  is_line_items_error_messages_present: bool = False