from pydantic import BaseModel
import datetime
from peewee import *

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

class PostFclFreightRateExtensionRuleSet(BaseModel):
  cluster_id: str = None
  cluster_reference_name: str = None
  cluster_type: str = None
  created_at: datetime.datetime = None
  extension_name: str = None
  gri_currency: str = None
  gri_rate: float
  line_item_charge_code: str = None
  service_provider_id: str = None
  shipping_line_id: str = None
  status: str = None
  trade_type: str = None
  updated_at: datetime.datetime = None

#class DestinationLocal(BaseModel):

class ExtendCreateFclFreightRate(BaseModel):
  performed_by_id: str
  procured_by_id: str
  sourced_by_id: str
  bulk_operation_id: str = None
  cogo_entity_id: str = None
  rate_sheet_id: str = None
  origin_port_id: str
  origin_main_port_id: str = None
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
  mandatory_charges: LocalData = None
  extend_rates: bool = False
  extend_rates_for_lens: bool = False
  extend_rates_for_existing_system_rates: bool = False

class UpdateFclFreightRateExtensionRuleSet(BaseModel):
  id: str
  performed_by_id: str
  extension_name: str = None
  service_provider_id: str = None
  shipping_line_id: str = None
  cluster_id: str = None
  cluster_type: str = None
  cluster_reference_name: str = None
  line_item_charge_code: str = None
  gri_currency: str = None
  gri_rate: float = None
  status: str = None
  trade_type: str = None

class ListFclFreightRateExtensionRuleSets(BaseModel):
  filters: dict = {}
  page_limit: int = 10
  page: int = 1
  sort_by: str = 'updated_at'
  sort_type: str = 'desc'

class GetFclFreightRateExtension(BaseModel):
  service_provider_id: str
  shipping_line_id: str
  origin_port_id: str
  destination_port_id: str
  commodity: str
  container_size: str
  container_type:str = None