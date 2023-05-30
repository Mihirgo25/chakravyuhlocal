from pydantic import BaseModel
from datetime import datetime, timedelta,date
from peewee import *
from typing import List
from dateutil.relativedelta import relativedelta

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
  location_type: str
  trade_type: str
  container_size: str
  container_type: str
  commodity: str = None
  service_provider_id: str
  performed_by_id: str
  sourced_by_id: str
  procured_by_id: str
  cargo_handling_type: str
  importer_exporter_id: str = None
  cfs_line_items: list[StandardLineItem]
  free_days: list[FreeDaysType]

class FclCfsRateRequest(BaseModel):
    source: str 
    source_id:str 
    performed_by_id : str
    performed_by_org_id: str
    performed_by_type: str
    preferred_rate: str= None
    preferred_rate_currency: str= None
    preferred_detention_free_days: str= None
    cargo_readiness_date: str= None
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
    validity_start: datetime
    validity_end: datetime
    bulk_operation_id: str = None
    sourced_by_id: str = None
    procured_by_id: str = None
    payment_term: str = 'prepaid'

class DeleteFclCfsRateRequest(BaseModel):
  fcl_freight_rate_request_ids: List[str]
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
