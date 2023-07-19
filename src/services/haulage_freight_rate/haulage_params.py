from pydantic import BaseModel
from datetime import datetime, timedelta, date
from peewee import *

class HaulageFreightRateWeightSlab(BaseModel):
  lower_limit: float
  upper_limit: float
  price: float
  currency: str
  remarks: list[str] = None

class HaulageLineItem(BaseModel):
  code: str
  unit: str
  price: float
  currency: str
  remarks: list[str] = None
  slabs: list[HaulageFreightRateWeightSlab] = None

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
  performed_by_id: str = None
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
  sourced_by_id: str= None
  bulk_operation_id: str = None
  id: str
  line_items: list[HaulageLineItem]
  performed_by_type: str = None


class CreateHaulageFreightRateRequest(BaseModel):
  source: str = "spot_search"
  source_id: str
  performed_by_id: str = None
  performed_by_org_id: str
  performed_by_type: str = "user"
  preferred_freight_rate: float = None
  preferred_freight_rate_currency: str = None
  preferred_detention_free_days: int = None
  cargo_readiness_date: date = None
  preferred_shipping_line_ids: list[str] = []
  remarks: list[str] = []
  booking_params: dict = {}
  containers_count: int
  container_size: str
  commodity: str = None
  cargo_weight_per_container: int
  destination_city_id: str = None
  destination_country_id: str = None
  destination_cluster_id: str = None
  destination_location_id: str
  origin_city_id: str = None
  origin_country_id: str = None
  origin_cluster_id: str = None
  origin_location_id: str
  container_type: str = None
  trade_type: str = None

class DeleteHaulageFreightRateRequest(BaseModel):
  haulage_freight_rate_request_ids: list[str]
  closing_remarks: list[str] = []
  rate_id: str = None
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
  dislikes_count: int = None
  likes_count: int = None
  performed_by_type: str = None
  preferred_freight_rate: float = None
  preferred_freight_rate_currency: str = None
  booking_params: dict = {}
  feedback_type: str
  status: str = None
  closing_remarks: list[str] = None
  closed_by_id: str = None
  serial_id: int = None
  origin_location_id: str = None
  origin_city_id: str = None
  origin_country_id: str = None
  destination_location_id: str = None
  destination_city_id: str = None
  destination_country_id: str = None
  origin_location: dict = None
  destination_location: dict = None
  container_size: str = None
  container_type: str = None
  commodity: str = None
  service_provider_id: str = None
  created_at: datetime = None
  updated_at: datetime = None

class RevertedRateParams(BaseModel):
    id: str = None
    line_items: list[HaulageLineItem] = []

class DeleteHaulageFreightRateFeedback(BaseModel):
  haulage_freight_rate_feedback_ids: list[str]
  closing_remarks: list[str] = []
  reverted_rate_id: str = None
  reverted_rate: RevertedRateParams = None
  performed_by_id: str = None
    
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
  filters: dict = {}

class AddMarkup(BaseModel):
  filters: dict = {}
  markup: float
  markup_type: str
  markup_currency: str = None

class CreateHaulageFreightRateBulkOperation(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  service_provider_id: str = None
  procured_by_id: str
  sourced_by_id: str = None
  delete_rate: DeleteRate = None
  add_markup: AddMarkup = None
  
class DeleteHaulageFreightRate(BaseModel):
  id: str
  performed_by_id: str = None
  performed_by_type: str = None
  bulk_operation_id: str = None
  sourced_by_id: str = None
  procured_by_id: str = None