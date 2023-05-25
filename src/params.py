from pydantic import BaseModel
from datetime import datetime, timedelta,date
from peewee import *
from typing import List
from dateutil.relativedelta import relativedelta


class Slab(BaseModel):
  lower_limit: float
  upper_limit: float
  price: float
  currency: str

class UpdateLineItem(BaseModel):
  code: str
  unit: str
  price: float
  market_price: float = None 
  currency: str
  remarks: list[str] = []
  slabs: list[Slab] = []


class FreeDay(BaseModel):
  free_limit: float
  slabs: list[Slab] = []
  remarks: list[str] = []

class LineItem(BaseModel):
  location_id: str = None
  code: str
  unit: str
  price: float
  currency: str
  market_price: float = None 
  remarks: list[str] = []
  slabs: list[Slab] = []

class LocalData(BaseModel):
  line_items: list[LineItem]=[]
  detention: FreeDay = None
  demurrage: FreeDay = None
  plugin: FreeDay = None


  
class PostFclFreightRate(BaseModel):
  origin_main_port_id: str = None
  origin_port_id: str
  destination_port_id: str
  destination_main_port_id: str = None
  container_size: str
  container_type: str
  commodity: str
  shipping_line_id: str = None
  service_provider_id: str = None
  importer_exporter_id: str = None
  validity_start: datetime
  validity_end: datetime
  schedule_type: str = 'transhipment'
  fcl_freight_rate_request_id: str = None
  payment_term: str = 'prepaid'
  line_items: List[UpdateLineItem]=[]
  weight_limit: FreeDay = None
  origin_local: LocalData = None
  destination_local: LocalData = None
  bulk_operation_id: str = None
  rate_sheet_id: str = None
  performed_by_id: str = None
  performed_by_type: str = None
  procured_by_id: str = None
  sourced_by_id: str = None
  cogo_entity_id: str = None
  mode: str = None
  source: str = 'rms_upload'
  is_extended: bool = None
  rate_not_available_entry: bool = False
  rate_type: str = 'market_place'
  available_inventory: int = 100
  used_inventory: int = 0
  shipment_count: int = 0
  volume_count: int = 0
  value_props: List[dict] = []
  t_n_c: list = []
  validities:List[dict] = None


class CreateFclFreightRateCommoditySurcharge(BaseModel):
  rate_sheet_id: str = None
  performed_by_id: str = None
  performed_by_type: str = None
  sourced_by_id: str
  procured_by_id: str
  origin_location_id: str
  destination_location_id: str
  container_size: str
  container_type: str
  commodity: str
  shipping_line_id: str
  service_provider_id: str
  price: int
  currency: str
  remarks: list[str] = []

class CreateFclFreightCommodityCluster(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  name: str
  commodities: dict

class UpdateFclFreightCommodityCluster(BaseModel):
  id: str
  performed_by_id: str = None
  performed_by_type: str = None
  name: str = None
  status: str = None
  commodities: dict = {}

class CreateFclFreightRateLocalAgent(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  service_provider_id: str
  status: str = 'active'
  location_id: str
  trade_type: str

class CreateFclWeightSlabsConfiguration(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  origin_location_id: str = None
  destination_location_id: str = None
  origin_location_type: str = None
  destination_location_type: str = None
  organization_category: str = None
  shipping_line_id: str = None
  service_provider_id: str = None
  importer_exporter_id: str = None
  is_cogo_assured: bool = False
  container_size: str = None
  commodity: str = None
  slabs: list[Slab] = []
  max_weight: float
  trade_type: str = None

class UpdateFclFreightRate(BaseModel):
  id: str
  procured_by_id: str = None
  sourced_by_id: str = None
  performed_by_id: str = None
  performed_by_type: str = None
  bulk_operation_id: str = None
  validity_start: datetime = None
  validity_end: datetime = None
  schedule_type: str = 'transhipment'
  payment_term: str = 'prepaid'
  line_items: list[UpdateLineItem] = []
  weight_limit: FreeDay = None
  origin_local: LocalData = None
  destination_local: LocalData = None
  source: str = 'rms_upload'
  is_extended: bool = None
  rate_type: str = "market_place"
  validities : List[dict] = []

class Data(BaseModel):
    line_items: list[LineItem] = []
    detention: FreeDay = None
    demurrage: FreeDay = None
    plugin: FreeDay = None

class PostFclFreightRateLocal(BaseModel):
    rate_sheet_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    procured_by_id: str = None
    sourced_by_id: str = None
    trade_type: str
    port_id: str = None
    country_id: str = None
    main_port_id: str = None
    container_size: str
    container_type: str
    commodity: str = None
    shipping_line_id: str
    service_provider_id: str
    selected_suggested_rate_id: str = None
    source: str = None
    data: Data = {}
    rate_not_available_entry: bool = False

class UpdateFclFreightRateLocal(BaseModel):
    id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    procured_by_id: str
    sourced_by_id: str
    bulk_operation_id: str = None
    selected_suggested_rate_id: str = None
    data: Data
    rate_not_available_entry: bool = False

class PostFclFreightRateExtensionRuleSet(BaseModel):
  cluster_id: str
  cluster_reference_name: str
  cluster_type: str
  extension_name: str
  gri_currency: str = None
  gri_rate: float = None
  line_item_charge_code: str = None
  service_provider_id: str = None
  shipping_line_id: str = None
  trade_type: str = None
  performed_by_id: str = None
  performed_by_type: str = None

class MandatoryCharges(BaseModel):
  line_items: list[UpdateLineItem] = []
  required_mandatory_codes: list[dict] = []

class ExtendCreateFclFreightRate(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
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
  validity_start: datetime
  validity_end: datetime
  schedule_type: str = 'transhipment'
  fcl_freight_rate_request_id: str = None
  payment_term: str = 'prepaid'
  line_items: List[UpdateLineItem]
  weight_limit: FreeDay = None
  origin_local: Data = None
  destination_local: Data = None
  mandatory_charges: MandatoryCharges = None
  extend_rates: bool = False
  extend_rates_for_lens: bool = False
  extend_rates_for_existing_system_rates: bool = False

class UpdateFclFreightRateExtensionRuleSet(BaseModel):
  id: str
  performed_by_id: str = None
  performed_by_type: str = None
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



class GetFclFreightRateLocal(BaseModel):
    port_id: str = None
    main_port_id: str = None
    trade_type: str = None
    container_size: str = None
    container_type: str = None
    commodity: str = None
    shipping_line_id: str = None
    service_provider_id: str = None

class GetFclFreightRateCard(BaseModel):
    origin_port_id: str
    origin_country_id: str
    destination_port_id: str
    destination_country_id: str
    container_size: str
    container_type: str
    commodity: str
    importer_exporter_id: str
    containers_count: int
    bls_count: int
    include_origin_local: bool
    include_destination_local: bool
    trade_type: str
    include_destination_dpd: bool
    cargo_weight_per_container: int = 0
    additional_services: List[str] = []
    validity_start: str
    validity_end: str
    ignore_omp_dmp_sl_sps: List[str] = []
    include_confirmed_inventory_rates: bool = False
    cogo_entity_id: str = None

class GetFclFreightLocalRateCards(BaseModel):
    trade_type: str
    port_id: str
    country_id: str
    shipping_line_id: str = None
    container_size: str
    container_type: str
    commodity: str = None
    containers_count: int
    bls_count: int
    cargo_weight_per_container: int = None
    include_destination_dpd: bool = False
    additional_services: List[str] = []
    include_confirmed_inventory_rates: bool = False
    rates: List[str] = []
    service_provider_id: str = None

class   DeleteFclFreightRate(BaseModel):
    id: str
    performed_by_id: str = None
    performed_by_type: str = None
    validity_start: datetime
    validity_end: datetime
    bulk_operation_id: str = None
    sourced_by_id: str = None
    procured_by_id: str = None
    payment_term: str = 'prepaid'
    rate_type:str = 'market_place'

class DeleteFclFreightRateFeedback(BaseModel):
    fcl_freight_rate_feedback_ids: List[str]
    closing_remarks: List[str] = []
    performed_by_id: str = None
    performed_by_type: str = None

class CreateFclFreightRateFeedback(BaseModel):
  source: str
  source_id: str
  performed_by_id: str = None
  performed_by_org_id: str
  performed_by_type: str = None
  rate_id: str
  validity_id: str
  likes_count: int
  dislikes_count: int
  feedbacks: list[str] = []
  remarks: list[str] = []
  preferred_freight_rate: float = None
  preferred_freight_rate_currency: str = None
  preferred_detention_free_days: int = None
  preferred_shipping_line_ids: list[str] = []
  feedback_type: str
  booking_params: dict = {}
  cogo_entity_id: str = None
  origin_port_id: str = None
  origin_trade_id: str = None
  origin_country_id: str = None
  origin_continent_id: str = None
  destination_port_id: str = None
  destination_continent_id: str = None
  destination_trade_id: str = None
  destination_country_id: str = None
  commodity: str = None
  container_size: str = None
  container_type: str = None
  service_provider_id: str = None
  attachment_file_urls: List[str] =[]
  commodity_description:str=None


class CreateFclFreightRateNotAvailable(BaseModel):
    origin_port_id: str
    origin_country_id: str = None
    origin_trade_id: str = None
    destination_port_id: str
    destination_country_id: str = None
    destination_trade_id: str = None
    container_size: str
    container_type: str
    commodity: str
    performed_by_id: str = None
    performed_by_type: str = None

class UpdateFclFreightRateLocalAgent(BaseModel):
  id: str
  performed_by_id: str = None
  performed_by_type: str = None
  status: str = None
  service_provider_id: str = None


class rate(BaseModel):
  line_items: list[LineItem] = []
  detention: FreeDay = None
  demurrage: FreeDay = None
  plugin: FreeDay = None

class CreateRateSheet(BaseModel):
    service_provider_id: str
    service_name: str
    partner_id: str = None
    cogo_entity_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    procured_by_id: str = None
    sourced_by_id: str = None
    comment: str = None
    file_url: str

class ConvertedFile(BaseModel):
    service_name: str = None
    module: str = None
    file_url: str = None
    rate_sheet_id: str = None
    service_provider_id: str = None
    cogo_entity_id: str = None
    file_index: int = None
    id: str = None
    status: str = None
    rates_count: int = None
    total_lines: int = None
    last_line: int = None


class UpdateRateSheet(BaseModel):
    performed_by_id: str = None
    performed_by_type: str = None
    procured_by_id: str = None
    sourced_by_id: str = None
    cogo_entity_id: str = None
    id: str
    converted_files: list[ConvertedFile] = []

class CreateFclFreightRateTask(BaseModel):
  service: str
  port_id: str
  main_port_id: str = None
  container_size: str
  container_type: str
  commodity: str
  trade_type: str
  shipping_line_id: str
  source: str
  task_type: str
  shipment_id: str = None
  performed_by_id: str = None
  performed_by_type: str = None
  rate: LocalData = None

class DeleteFclFreightRateRequest(BaseModel):
  fcl_freight_rate_request_ids: List[str]
  closing_remarks: List[str] = []
  performed_by_id: str = None
  performed_by_type: str = None

class CreateFclFreightRateWeightLimit(BaseModel):
  rate_sheet_id: str = None
  performed_by_id: str = None
  performed_by_type: str = None
  sourced_by_id: str
  procured_by_id: str
  origin_location_id: str
  destination_location_id: str
  container_size: str
  container_type: str
  shipping_line_id: str
  service_provider_id: str
  free_limit: float
  remarks: list[str] = []
  slabs: list[Slab] = []

class DeleteFclFreightRateLocalRequest(BaseModel):
  fcl_freight_rate_local_request_ids: List[str]
  closing_remarks: List[str] = []
  performed_by_id: str = None
  performed_by_type: str = None
class UpdateFclFreightRateWeightLimit(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  procured_by_id: str
  sourced_by_id: str
  id: str
  free_limit: int = None
  remarks: list[str] = []
  slabs: list[Slab] = []

class DeleteFclFreightRateLocal(BaseModel):
  id: str
  performed_by_id: str = None
  performed_by_type: str = None
  bulk_operation_id: str = None
  sourced_by_id: str
  procured_by_id: str
class CreateFclFreightRateFreeDay(BaseModel):
  rate_sheet_id: str = None
  performed_by_id: str = None
  performed_by_type: str = None
  sourced_by_id: str = None
  procured_by_id: str = None
  trade_type: str
  location_id: str
  free_days_type: str
  container_size: str
  container_type: str
  shipping_line_id: str
  service_provider_id: str
  importer_exporter_id: str = None
  specificity_type: str
  previous_days_applicable: bool = False
  free_limit: int
  remarks: list[str] = []
  slabs: list[Slab] = []
  validity_start: datetime = datetime.now()
  validity_end: datetime = (datetime.now() + timedelta(days=90))

class DeleteFclFreightRateFreeDayRequest(BaseModel):
  fcl_freight_rate_free_day_request_id: str
  closing_remarks: List[str] = []
  performed_by_id: str = None
  performed_by_type: str = None
class UpdateFclFreightRateFreeDay(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  bulk_operation_id: str = None
  procured_by_id: str = None
  sourced_by_id: str = None
  id: str
  free_limit: int = None
  validity_start: datetime = datetime.now()
  validity_end: datetime = datetime.now() + relativedelta(months=3)
  hs_code: str = None
  remarks: list[str] = []
  slabs: list[Slab] = []
class CreateFclFreightRateRequest(BaseModel):
  source: str
  source_id: str
  cogo_entity_id: str
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
  inco_term: str
  commodity: str = None
  cargo_weight_per_container: int
  destination_continent_id: str = None
  destination_country_id: str = None
  destination_port_id: str
  destination_trade_id: str = None
  origin_continent_id: str = None
  origin_country_id: str = None
  origin_port_id: str
  origin_trade_id: str = None
  container_type: str = None
  attachment_file_urls:List[str]=[]
  commodity_description:str=None


class CreateFclFreightRateLocalRequest(BaseModel):
  source: str
  source_id: str
  performed_by_id: str = None
  performed_by_org_id: str
  performed_by_type: str = None
  preferred_rate: float = None
  preferred_rate_currency: str = None
  country_id: str = None
  shipping_line_id: str = None
  continent_id: str = None
  container_size: str = None
  cargo_readiness_date: datetime = None
  preferred_shipping_line_ids: list[str] = []
  remarks: list[str] = []
  booking_params: dict = {}
  containers_count: int = None
  commodity: str = None
  cargo_weight_per_container: int = None
  container_type: str = None
  port_id: str = None
  main_port_id: str = None
  trade_id: str = None
  trade_type: str = None

class CreateFclFreightRateFreeDayRequest(BaseModel):
  source: str
  source_id: str
  performed_by_id: str = None
  performed_by_org_id: str
  performed_by_type: str = None
  trade_type: str
  location_id: str
  free_days_type: str
  code: str
  country_id: str = None
  trade_id: str = None
  continent_id: str = None
  main_port_id: str = None
  containers_count: int = None
  container_size: str = None
  container_type: str = None
  commodity: str = None
  shipping_line_id: str = None
  service_provider_id: str = None
  inco_term: str = None
  cargo_readiness_date: datetime = None
  cargo_weight_per_container: int = None
  preferred_rate: float = None
  preferred_rate_currency: str = None
  preferred_free_days: int = None
  preferred_total_days: int = None
  specificity_type: str = None
  booking_params: dict = {}
  remarks: list[str] = []

class UpdateFclWeightSlabsConfiguration(BaseModel):
  id: str = None
  max_weight: float = None
  status: str = None
  trade_type: str = None
  container_size: str = None
  commodity: str = None
  organization_category: str = None
  destination_location_type: str = None
  origin_location_type: str = None
  origin_location_id: str = None
  destination_location_id: str = None
  shipping_line_id: str = None
  service_provider_id: str = None
  importer_exporter_id: str = None
  is_cogo_assured: bool =False
  slabs: list[Slab] = []
  performed_by_id: str = None
  performed_by_type: str = None

class UpdateFclFreightRatePlatformPrices(BaseModel):
  origin_port_id: str
  origin_main_port_id:str = None
  destination_port_id: str
  destination_main_port_id: str = None
  container_size: str
  container_type: str
  commodity: str
  shipping_line_id: str
  importer_exporter_id: str = None
  performed_by_id: str = None
  performed_by_type: str = None

class CreateFclFreightRateWeightLimit(BaseModel):
  rate_sheet_id: str = None
  performed_by_id: str = None
  sourced_by_id: str
  procured_by_id: str
  origin_location_id: str
  destination_location_id: str
  container_size: str
  container_type: str
  shipping_line_id: str
  service_provider_id: str
  free_limit: float
  remarks: list[str] = []
  slabs: list[Slab] = []
  performed_by_id: str = None
  performed_by_type: str = None

class UpdateFclFreightRateCommoditySurcharge(BaseModel):
  performed_by_id: str = None
  procured_by_id: str
  sourced_by_id: str
  id: str
  price: int
  currency: str
  remarks: list[str] = []
  performed_by_type: str = None

class CreateFclFreightCommoditySurcharge(BaseModel):
  rate_sheet_id: str = None
  performed_by_id: str = None
  performed_by_type: str = None
  sourced_by_id: str
  procured_by_id: str
  origin_location_id: str
  destination_location_id: str
  container_size: str
  container_type: str
  shipping_line_id: str
  service_provider_id: str
  commodity: str
  price: int
  currency: str
  remarks: list[str] = []

class CreateFclFreightSeasonalSurcharge(BaseModel):
  rate_sheet_id: str = None
  performed_by_id: str = None
  performed_by_type: str = None
  sourced_by_id: str
  procured_by_id: str
  origin_location_id: str
  destination_location_id: str
  container_size: str
  container_type: str
  shipping_line_id: str
  service_provider_id: str
  code: str
  price: int
  currency: str
  remarks: list[str] = []
  validity_start: datetime = None
  validity_end: datetime = None

class CreateFclFreightCommoditySurcharge(BaseModel):
  rate_sheet_id: str = None
  performed_by_id: str = None
  performed_by_type: str = None
  sourced_by_id: str
  procured_by_id: str
  origin_location_id: str
  destination_location_id: str
  container_size: str
  container_type: str
  shipping_line_id: str
  service_provider_id: str
  commodity: str
  price: int
  currency: str
  remarks: list[str] = []

class CreateFclFreightSeasonalSurcharge(BaseModel):
  rate_sheet_id: str = None
  performed_by_id: str = None
  performed_by_type: str = None
  sourced_by_id: str
  procured_by_id: str
  origin_location_id: str
  destination_location_id: str
  container_size: str
  container_type: str
  shipping_line_id: str
  service_provider_id: str
  code: str
  price: int
  currency: str
  remarks: list[str] = []
  validity_start: datetime = None
  validity_end: datetime = None

class ExtendValidty(BaseModel):
  filters:dict={}
  source_date:datetime
  validity_end:datetime
  sourced_by_ids:dict=None
  procured_by_ids:dict=None

class DeleteFreightRate(BaseModel):
  filters:dict={}
  validity_start: datetime
  validity_end: datetime

class AddFreightRateMarkup(BaseModel):
  filters:dict={}
  markup:float
  markup_type:str
  markup_currency:str=None
  line_item_code:str='BAS'
  validity_start:datetime
  validity_end:datetime

class AddLocalRateMarkup(BaseModel):
  filters:dict={}
  markup:float
  markup_type:str
  markup_currency:str=None
  line_item_code:str

class ExtendFreightRateToIcds(BaseModel):
  filters: dict={}
  markup_type : str
  markup : float
  markup_currency:str = None
  line_item_code : str = 'BAS'
  origin_port_ids : List[str] = []
  destination_port_ids : List[str] = []

class ExtendFreightRate(BaseModel):
  filters: dict = {}
  commodities : List[str] = []
  container_sizes : List[str] = []
  container_types:List[str] = []
  markup_type : str
  markup : float
  markup_currency : str = None
  line_item_code : str = 'BAS '
class UpdateWeightLimit(BaseModel):
  filters: dict={}
  free_limit : int
  slabs : List[Slab] = None
class UpdateFreeDays(BaseModel):
  filters: dict={}
  free_days_type:str
  free_limit : int
  slabs : List[Slab] = None

class AddFreightLineItem(BaseModel):
  filters : dict = {}
  code : str
  unit : str
  price : float
  currency : str
  validity_start : datetime
  validity_end : datetime
class UpdateFreeDaysLimit(BaseModel):
  filters: dict={}
  free_limit : int
  slabs : List[Slab] = []

class DeleteLocalRate(BaseModel):
  filters : dict={}

class CreateBulkOperation(BaseModel):
  performed_by_id: str = None
  performed_by_type: str = None
  service_provider_id:str
  procured_by_id:str
  sourced_by_id:str
  cogo_entity_id:str=None
  extend_validity:ExtendValidty=None
  delete_freight_rate:DeleteFreightRate=None
  add_freight_rate_markup:AddFreightRateMarkup=None
  add_local_rate_markup:AddLocalRateMarkup=None
  delete_local_rate:DeleteLocalRate=None
  update_free_days_limit:UpdateFreeDaysLimit=None
  add_freight_line_item:AddFreightLineItem=None
  update_free_days:UpdateFreeDays=None
  update_weight_limit:UpdateWeightLimit=None
  extend_freight_rate:ExtendFreightRate=None
  extend_freight_rate_to_icds:ExtendFreightRateToIcds=None

class UpdateFclFreightRateTask(BaseModel):
  id: str
  performed_by_id: str=None
  performed_by_type: str=None
  rate: LocalData = None
  status: str = None
  closing_remarks: str = None
  validate_closing_remarks: str = None

class UpdateRateProperties(BaseModel):
  rate_id:str
  available_inventory: int = 100
  used_inventory: int = 0
  shipment_count: int = 0
  volume_count: int = 0
  value_props: List[dict] = []
  t_n_c: List[str] = []
