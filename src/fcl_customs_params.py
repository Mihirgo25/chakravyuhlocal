from pydantic import BaseModel
from peewee import *
from typing import List

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