from pydantic import BaseModel
from datetime import datetime
from peewee import *
from typing import List
from params import *

class CreateDraftFclFreightRate(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  rate_id : str
  data : List[StandardLineItem]=None
  source : str
  status : str = 'pending'
  invoice_url : str = None
  invoice_date : datetime = None
  shipment_serial_id : str = None

class CreateFclFreightDraft(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  rate_id : str
  status : str = 'pending'
  data : List[StandardLineItem]=None
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
  importer_exporter_id: str = None
  validity_start: datetime
  validity_end: datetime
  schedule_type: str = 'transhipment'
  fcl_freight_rate_request_id: str = None
  payment_term: str = 'prepaid'
  line_items: List[StandardLineItem]=None
  weight_limit: FreeDay = None
  origin_local: LocalData = None
  destination_local: LocalData = None
  bulk_operation_id: str = None
  rate_sheet_id: str = None
  procured_by_id: str = None
  sourced_by_id: str
  cogo_entity_id: str = None
  mode: str = None
  source: str = None
  is_extended: bool = None
  rate_not_available_entry: bool = False
class UpdateDraftFclFreightRate(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  id : str
  rate_id : str = None
  data : List[StandardLineItem]=None
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
  data: Data = {}
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
  data: Data = {}
  rate_not_available_entry: bool = False

class UpdateDraftFclFreightRateLocal(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  id : str
  rate_id : str = None
  data : Data = {}
  source : str = None
  status : str = 'pending'
  invoice_url : str = None
  invoice_date : datetime = None
  shipment_serial_id : str = None