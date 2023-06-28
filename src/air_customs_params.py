from pydantic import BaseModel
from peewee import *
from typing import List
from datetime import date

class AirCustomsLineItems(BaseModel):
    code: str
    unit: str
    price: float
    currency: str
    remarks: list[str] = None

class DeleteRate(BaseModel):
  air_customs_rate_id: str

class AddMarkup(BaseModel):
  air_customs_rate_id: str
  markup: float
  markup_type: str    
  markup_currency: str = None
  
class CreateAirCustomsRateBulkOperation(BaseModel):
  performed_by_id: str
  performed_by_type: str
  procured_by_id: str = None
  sourced_by_id: str = None
  delete_rate: List[DeleteRate] = None
  add_markup: List[AddMarkup] = None

class CreateAirCustomsRateFeedback(BaseModel):
  source: str
  source_id: str
  performed_by_id: str
  performed_by_org_id: str
  performed_by_type: str
  rate_id: str
  likes_count: int
  dislikes_count: int
  feedbacks: list[str] = []
  remarks: list[str] = []
  preferred_customs_rate: float = None
  preferred_customs_rate_currency: str = None
  feedback_type: str
  booking_params: dict ={}
  airport_id: str = None
  country_id: str = None
  trade_type: str = None
  trade_id: str = None
  commodity: str = None
  service_provider_id: str = None

class CreateAirCustomsRateNotAvailable(BaseModel):
  airport_id: str
  country_id: str
  trade_type: str
  commodity: str = None
  performed_by_type: str
  performed_by_id: str

class CreateAirCustomsRateRequest(BaseModel):
  source: str
  source_id: str
  performed_by_id: str
  performed_by_org_id: str
  performed_by_type: str
  preferred_customs_rate: float = None
  preferred_customs_rate_currency: str = None
  # preferred_detention_free_days: int = None
  # preferred_storage_free_days: int = None
  cargo_readiness_date: date = None
  remarks: list[str] = []
  booking_params: dict = {}
  weight: float
  volume: float
  commodity: str = None
  country_id: str = None
  airport_id: str 
  continent_id: str 
  city_id: str = None
  trade_type: str = None

class CreateAirCustomsRate(BaseModel):
  rate_sheet_id: str = None
  airport_id: str
  trade_type: str
  commodity: str = 'all_commodities'
  service_provider_id: str
  performed_by_id: str = None
  sourced_by_id: str
  procured_by_id: str
  importer_exporter_id: str = None
  line_items: List[AirCustomsLineItems] = None
  performed_by_type: str = None
  bulk_operation_id: str = None
  rate_type: str = 'general'


class UpdateAirCustomsRatePlatformPrices(BaseModel):
  location_id: str
  container_size: str 
  container_type: str 
  commodity: str = None
  trade_type:str
  performed_by_id: str
  performed_by_type: str
  importer_exporter_id: str = None
  is_customs_line_items_error_messages_present: bool = False
  is_cfs_line_items_error_messages_present: bool = False


class DeleteAirCustomsRateFeedback(BaseModel):
 air_customs_rate_feedback_ids: list[str] 
 closing_remarks: list[str] = []
 performed_by_id: str
 performed_by_type: str


class DeleteAirCustomsRateRequest(BaseModel):
 air_customs_rate_request_ids: list[str] 
 closing_remarks: list[str] = []
 performed_by_id: str
 performed_by_type: str  

class UpdateAirCustomsRate(BaseModel):
  id: str
  performed_by_id: str
  sourced_by_id: str
  procured_by_id: str
  bulk_operation_id: str = None
  performed_by_type: str = None
  line_items: list[AirCustomsLineItems] = None

class DeleteAirCustomsRateFeedback(BaseModel):
 air_customs_rate_feedback_ids: list[str] 
 closing_remarks: list[str] = []
 performed_by_id: str
 performed_by_type: str = None

class DeleteAirCustomsRate(BaseModel):
  id: str
  performed_by_id: str
  performed_by_type: str = None
  bulk_operation_id: str = None

class DeleteAirCustomsRateRequest(BaseModel):
  air_customs_rate_request_ids: list[str] 
  closing_remarks: list[str] = []
  performed_by_id: str
  performed_by_type: str = None