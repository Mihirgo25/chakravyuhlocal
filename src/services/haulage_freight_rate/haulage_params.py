from pydantic import BaseModel
from datetime import datetime, timedelta, date
from peewee import *

from params import Slab

class HaulageLineItem(BaseModel):
  code: str
  unit: str
  price: float
  currency: str
  remarks: list[str] = None
  slabs: list[Slab] = None

class CreateHaulageFreightRate(BaseModel):
  rate_sheet_id: str = None
  origin_location_id: str 
  destination_location_id: str
  container_size: str
  container_type: str
  commodity: str = None
  service_provider_id: str
  shipping_line_id: str = None
  haulage_type: str 
  performed_by_id: str
  performed_by_type: str = None
  procured_by_id: str 
  sourced_by_id: str 
  importer_exporter_id: str = None
  transit_time: int = None
  detention_free_time: int = None
  validity_start: datetime = datetime.now()
  validity_end: datetime = (datetime.now() + timedelta(days=90))
  trailer_type: str = None
  trip_type: str = None
  transport_modes: list[str]=None
  line_items: list[HaulageLineItem]
  haulage_freight_rate_request_id: str = None


class UpdateHaulageFreightRate(BaseModel):
  performed_by_id: str = None
  procured_by_id: str = None
  sourced_by_id: str = None
  bulk_operation_id: str = None
  id: str = None
  line_items: list[HaulageLineItem]


class CreateHaulageFreightRateRequest(BaseModel):
  source: str
  source_id: str
  performed_by_id: str = None
  performed_by_org_id: str
  performed_by_type: str = None
  preferred_freight_rate: float = None
  preferred_freight_rate_currency: str = None
  preferred_detention_free_days: int = None
  preferred_storage_free_days: int = None
  cargo_readiness_date: date = None
  preferred_shipping_line_ids: list[str] = []
  remarks: list[str] = []
  booking_params: dict = {}
  containers_count: int
  container_size: str
  commodity: str = None
  cargo_weight_per_container: int
  destination_continent_id: str = None
  destination_country_id: str = None
  destination_location_id: str
  destination_trade_id: str = None
  origin_continent_id: str = None
  origin_country_id: str = None
  origin_location_id: str
  origin_trade_id: str = None
  container_type: str = None

class DeleteHaulageFreightRateRequest(BaseModel):
  haulage_freight_rate_request_ids: list[str]
  closing_remarks: list[str] = []
  performed_by_id: str = None
  performed_by_type: str = None

class CreateHaulageFreightRateFeedback(BaseModel):
  source: str
  source_id: str
  feedbacks: list[str]=None
  remarks: list[str] = []
  haulage_freight_rate_id: str = None
  performed_by_id: str = None
  performed_by_org_id: str
  performed_by_type: str = None
  preferred_freight_rate: float = None
  preferred_freight_rate_currency: str = None
  outcome: str = None
  outcome_object_id: str = None
  booking_params: dict = {}
  feedback_type: str
  status: str = None
  closing_remarks: list[str] = None
  closed_by_id: str = None
  serial_id: int = None
  created_at: datetime = None
  updated_at: datetime = None

class DeleteHaulageFreightRateFeedback(BaseModel):
  haulage_freight_rate_feedback_ids: list[str]
  closing_remarks: list[str] = []
  performed_by_id: str = None
  performed_by_type: str = None
    
class UpdateHaulageFreightRatePlatformPrices(BaseModel):
  origin_location_id: str
  destination_location_id: str
  container_size: str
  container_type: str
  commodity: str = None
  haulage_type: str  
  shipping_line_id: str = None
  importer_exporter_id: str = None
  is_line_items_error_messages_present: bool = False
  performed_by_id: str = None
  performed_by_type: str = None


class CreateHaulageFreightRateNotAvailable(BaseModel):
  origin_location_id: str
  origin_country_id: str = None
  destination_location_id: str
  destination_country_id: str = None
  container_size: str
  container_type: str
  commodity: str = None
  haulage_type: str
  shipping_line_id: str = None
  transport_modes: list[str]=None

class DeleteRate(BaseModel):
  filters: dict = None

class AddMarkup(BaseModel):
  filters: dict = None
  markup: float
  markup_type: str
  markup_currency: str = None

class CreateHaulageFreightRateBulkOperation(BaseModel):
  performed_by_id: str
  service_provider_id: str = None
  procured_by_id: str
  sourced_by_id: str = None
  delete_rate: DeleteRate = None
  add_markup: AddMarkup = None

class DeleteHaulageFreightRate(BaseModel):
  id: str
  performed_by_id: str = None
  bulk_operation_id: str = None
  sourced_by_id: str = None
  procured_by_id: str = None