from pydantic import BaseModel
import datetime

class Slab(BaseModel):
  lower_limit: float
  upper_limit: float
  price: float
  currency: str

class UpdateLineItem(BaseModel):
  code: str
  unit: str
  price: float
  currency: str
  remarks: list[str] = []

class FreeDay(BaseModel):
  free_limit: int
  slabs: list[Slab] = None
  remarks: list[str] = None

class LineItem(BaseModel):
  location_id: str = None
  code: str
  unit: str
  price: float
  currency: str
  remarks: list[str] = []
  slabs: list[Slab] = None

class LocalData(BaseModel):
  line_items: list[LineItem] = None
  detention: FreeDay = None
  demurrage: FreeDay = None
  plugin: FreeDay = None

class StandardLineItem(BaseModel):
  code: str
  unit: str
  price: float
  currency: str
  remarks: list[str] = []
  slabs: list[Slab] = None

class PostFclFreightRate(BaseModel):
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
  validity_start: datetime.datetime
  validity_end: datetime.datetime
  schedule_type: str = 'transhipment'
  fcl_freight_rate_request_id: str = None
  payment_term: str = 'prepaid'
  line_items: list[StandardLineItem]
  weight_limit: FreeDay = None
  origin_local: LocalData = None
  destination_local: LocalData = None
  bulk_operation_id: str = None
  rate_sheet_id: str = None
  performed_by_id: str = None #remove this and below None
  procured_by_id: str = None
  sourced_by_id: str = None

class UpdateFclFreightRate(BaseModel):
  id: str
  procured_by_id: str = None #not null
  sourced_by_id: str = None #not null
  performed_by_id: str = None #not null
  bulk_operation_id: str = None
  validity_start: datetime.datetime = None
  validity_end: datetime.datetime = None
  schedule_type: str = 'transhipment'
  payment_term: str = 'prepaid'
  line_items: list[UpdateLineItem] = None
  weight_limit: FreeDay = None
  origin_local: LocalData = None
  destination_local: LocalData = None

class Data(BaseModel):
    line_items: list[LineItem] = None
    detention: FreeDay = None
    demurrage: FreeDay = None
    plugin: FreeDay = None

class PostFclFreightRateLocal(BaseModel):
    rate_sheet_id: str = None
    performed_by_id: str = None
    procured_by_id: str = None
    sourced_by_id: str = None
    trade_type: str
    port_id: str
    main_port_id: str = None
    container_size: str
    container_type: str
    commodity: str = None
    shipping_line_id: str
    service_provider_id: str
    selected_suggested_rate_id: str = None
    source: str = None
    data: Data

class UpdateFclFreightRateLocal(BaseModel):
    id: str = None
    performed_by_id: str = None #should be not null
    procured_by_id: str = None #should be not null
    sourced_by_id: str = None #should be not null
    bulk_operation_id: str = None
    selected_suggested_rate_id: str = None
    data: Data