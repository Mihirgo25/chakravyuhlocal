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