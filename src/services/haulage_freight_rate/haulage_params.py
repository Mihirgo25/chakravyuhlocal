from pydantic import BaseModel
from datetime import datetime, timedelta
from peewee import *

from params import Slab

class HaulageLineItem(BaseModel):
  location_id: str = None
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
  performed_by_id: str = None
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
