from pydantic import BaseModel
from peewee import *
from typing import List
from datetime import date
class FclCustomsLineItems(BaseModel):
    location_id: str = None
    code: str
    unit: str
    price: float
    currency: str
    remarks: list[str] = None
    condition: list[str] = None

class CreateFclCustomsRate(BaseModel):
  rate_sheet_id: str = None
  location_id: str
  trade_type: str
  container_size: str
  container_type: str
  commodity: str = None
  service_provider_id: str
  performed_by_id: str
  sourced_by_id: str
  procured_by_id: str
  importer_exporter_id: str = None
  customs_line_items: List[FclCustomsLineItems] = []

class DeleteRate(BaseModel):
  filters:dict={}

class AddMarkup(BaseModel):
  filters: dict = {}
  markup: float
  line_item_code: str = 'CCO'
  markup_type: str    
  markup_currency: str = None

class CreateFclCustomsRateBulkOperation(BaseModel):
  performed_by_id: str
  service_provider_id: str
  sourced_by_id: str
  procured_by_id: str
  delete_rate: DeleteRate = None
  add_markup: AddMarkup = None

class CreateFclCustomsRateNotAvailable(BaseModel):
  location_id: str
  country_id: str = None
  trade_type: str
  container_size: str
  container_type: str
  commodity: str = None

class CreateFclCustomsRateRequest(BaseModel):
  source: str
  source_id: str
  performed_by_id: str
  performed_by_org_id: str
  performed_by_type: str
  preferred_customs_rate: float = None
  preferred_customs_rate_currency: str = None
  preferred_detention_free_days: int = None
  preferred_storage_free_days: int = None
  cargo_readiness_date: date = None
  remarks: list[str] = []
  booking_params: dict = {}
  containers_count: int
  container_size: str 
  commodity: str = None
  cargo_handling_type: str 
  country_id: str = None
  port_id: str 
  container_type: str 
  trade_type: str = None

class UpdateFclCustomsRatePlatformPrices(BaseModel):
  location_id: str
  container_size: str 
  container_type: str 
  commodity: str = None
  importer_exporter_id: str = None
  is_customs_line_items_error_messages_presen: bool = False
  is_cfs_line_items_error_messages_presen: bool = False

class DeleteFclCustomsRateFeedback(BaseModel):
 fcl_customs_rate_feedback_ids: list[str] 
 closing_remarks: list[str] = []
 performed_by_id: str

class UpdateFclCustomsRate(BaseModel):
  id: str
  performed_by_id: str
  sourced_by_id: str
  procured_by_id: str
  bulk_operation_id: str = None
  customs_line_items: list[FclCustomsLineItems] = []
  cfs_line_items: list[FclCustomsLineItems] = []

class DeleteFclCustomsRate(BaseModel):
  id: str
  performed_by_id: str
  bulk_operation_id: str = None
  sourced_by_id: str
  procured_by_id: str