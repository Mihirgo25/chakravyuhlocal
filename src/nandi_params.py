from pydantic import BaseModel
from datetime import datetime
from peewee import *
from typing import List
from params import *

class DraftLocalData(BaseModel):
  line_items: list[LineItem] = []
  detention: FreeDay = None
  demurrage: FreeDay = None
  plugin: FreeDay = None
  origin_port: dict = None
  destination_port: dict = None
  origin_main_port: dict = None
  destination_main_port: dict = None

class CreateDraftFclFreightRate(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  rate_id : str
  data : List[UpdateLineItem]=None
  source : str
  status : str = 'pending'
  invoice_url : str = None
  invoice_date : datetime = None
  shipment_serial_id : str = None
  rate_type: str = 'market_place'

class CreateFclFreightDraft(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  status : str = 'pending'
  data : List[UpdateLineItem]=None
  invoice_url : str = None
  invoice_date : datetime = None
  shipment_serial_id : str = None
  origin_main_port_id: str = None
  origin_port_id: str
  destination_port_id: str
  destination_main_port_id: str = None
  container_size: str
  container_type: str
  commodity: str
  shipping_line_id: str
  service_provider_id: str
  validity_start: datetime
  validity_end: datetime
  line_items: List[UpdateLineItem]=None
  weight_limit: FreeDay = None
  procured_by_id: str = None
  sourced_by_id: str
  source: str = None
  rate_not_available_entry: bool = False
  rate_type: str = 'market_place'

class UpdateDraftFclFreightRate(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  id : str
  rate_id : str = None
  data : List[UpdateLineItem]=None
  source : str = None
  status : str = 'pending'
  invoice_url : str = None
  invoice_date : datetime = None
  shipment_serial_id : str = None

class CreateDraftFclFreightRateLocal(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  commodity : str = None
  container_size: str
  container_type: str
  rate_id : str
  data: DraftLocalData = {}
  source : str
  status : str = 'pending'
  invoice_url : str = None
  invoice_date : datetime = None
  main_port_id : str = None
  port : dict = None
  port_id : str = None
  shipping_line : dict = None
  shipping_line_id : str = None
  trade_type : str
  shipment_serial_id : str = None

class CreateFclFreightDraftLocal(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  container_size: str
  container_type: str
  commodity: str = None
  status : str = 'pending'
  invoice_url : str = None
  invoice_date : datetime = None
  port : dict = None
  shipping_line : dict = None
  shipment_serial_id : str = None
  procured_by_id: str = None
  sourced_by_id: str = None
  trade_type: str
  port_id: str
  main_port_id: str = None
  shipping_line_id: str
  service_provider_id: str
  selected_suggested_rate_id: str = None
  source: str = None
  data: DraftLocalData = {}
  rate_not_available_entry: bool = False

class UpdateDraftFclFreightRateLocal(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  id : str
  rate_id : str = None
  data : DraftLocalData = {}
  source : str = None
  status : str = 'pending'
  invoice_url : str = None
  invoice_date : datetime = None
  shipment_serial_id : str = None