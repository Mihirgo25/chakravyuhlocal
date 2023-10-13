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

class CreateFclCustomsRate(BaseModel):
  rate_sheet_id: str = None
  location_id: str
  trade_type: str
  container_size: str
  container_type: str
  commodity: str = None
  service_provider_id: str
  performed_by_id: str = None
  sourced_by_id: str
  procured_by_id: str
  importer_exporter_id: str = None
  customs_line_items: List[FclCustomsLineItems] = None
  cfs_line_items: List[FclCustomsLineItems] = None
  performed_by_type: str = None
  mode: str = None
  rate_type: str = 'market_place'

class DeleteRate(BaseModel):
  filters:dict={}

class AddMarkup(BaseModel):
  filters: dict = {}
  markup: float
  line_item_code: str = 'CCO'
  markup_type: str
  markup_currency: str = None

class CreateFclCustomsRateBulkOperation(BaseModel):
  performed_by_id: str = None
  service_provider_id: str
  sourced_by_id: str
  procured_by_id: str
  delete_rate: DeleteRate = None
  add_markup: AddMarkup = None
  performed_by_type: str = None

class CreateFclCustomsRateNotAvailable(BaseModel):
  location_id: str
  country_id: str = None
  trade_type: str
  container_size: str
  container_type: str
  commodity: str = None
  performed_by_type: str = None
  performed_by_id: str = None

class CreateFclCustomsRateRequest(BaseModel):
  source: str
  source_id: str
  performed_by_id: str = None
  performed_by_org_id: str
  performed_by_type: str = None
  preferred_customs_rate: float = None
  preferred_customs_rate_currency: str = None
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

class CreateFclCustomsRateFeedback(BaseModel):
  source: str
  source_id: str
  performed_by_id: str = None
  performed_by_org_id: str
  performed_by_type: str = None
  rate_id: str
  likes_count: int
  dislikes_count: int
  feedbacks: list[str] = []
  remarks: list[str] = []
  preferred_customs_rate: float = None
  preferred_customs_rate_currency: str = None
  feedback_type: str
  booking_params: dict ={}
  port_id: str = None
  country_id: str = None
  trade_type: str = None
  trade_id: str = None
  commodity: str = None
  service_provider_id: str = None

class UpdateFclCustomsRatePlatformPrices(BaseModel):
  location_id: str
  container_size: str
  container_type: str
  commodity: str = None
  trade_type:str
  performed_by_id: str = None
  performed_by_type: str = None
  importer_exporter_id: str = None
  is_customs_line_items_error_messages_present: bool = False
  is_cfs_line_items_error_messages_present: bool = False


class DeleteFclCustomsRateFeedback(BaseModel):
 fcl_customs_rate_feedback_ids: list[str]
 closing_remarks: list[str] = []
 performed_by_id: str = None
 performed_by_type: str = None
 reverted_rate: dict = {}

class DeleteFclCustomsRateRequest(BaseModel):
 fcl_customs_rate_request_ids: list[str]
 closing_remarks: list[str] = []
 performed_by_id: str = None
 performed_by_type: str  = None

class UpdateFclCustomsRate(BaseModel):
  id: str
  performed_by_id: str = None
  sourced_by_id: str
  procured_by_id: str
  bulk_operation_id: str = None
  performed_by_type: str = None
  customs_line_items: list[FclCustomsLineItems] = None
  cfs_line_items: list[FclCustomsLineItems] = None
  rate_type: str = 'market_place'

class DeleteFclCustomsRate(BaseModel):
  id: str
  sourced_by_id: str
  procured_by_id: str
  performed_by_id: str = None
  performed_by_type: str = None
  bulk_operation_id: str = None
  rate_type: str = 'market_place'

class CreateFclCustomsRateJob(BaseModel):
    source: str = None
    source_id: str = None
    shipment_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    location_id: str = None
    service_provider_id: str = None
    container_size: str = None
    container_type: str = None
    commodity: str = None
    trade_type: str = None
    is_visible: bool = True
    rate_type: str = None
    port_id: str = None

class DeleteFclCustomsRateJob(BaseModel):
    id: str = None
    closing_remarks: str = None
    data: dict = {}
    source_id: str = None
    shipment_id: str = None
    rate_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    
class UpdateFclCustomsRateJob(BaseModel):
    id: str
    user_id: str
    performed_by_id: str = None
    performed_by_type: str = None