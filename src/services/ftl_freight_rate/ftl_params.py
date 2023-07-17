from pydantic import BaseModel
from peewee import *
from typing import Optional,List
from datetime import datetime

class CreateTruck(BaseModel):
  truck_company: str
  display_name: str
  performed_by_id: Optional[str]=None
  performed_by_type: str=None
  mileage: float
  mileage_unit: str
  capacity: float
  capacity_unit: str
  vehicle_weight: float
  vehicle_weight_unit: str
  fuel_type: str
  avg_speed: float
  no_of_wheels: int
  engine_type: str = None
  country_id: str
  axels: int = None
  truck_type: str
  body_type: str = None
  status: str = None
  horse_power: float = None
  data: dict = {}

class UpdateTruck(BaseModel):
    id: int
    performed_by_id: Optional[str]=None
    performed_by_type: str=None
    mileage: float=None
    mileage_unit: str=None
    capacity: float=None
    capacity_unit: str=None
    vehicle_weight: float=None
    vehicle_weight_unit: str=None
    fuel_type: str=None
    avg_speed: float=None
    no_of_wheels: int=None
    engine_type: str=None
    axels: int=None
    truck_type: str=None
    body_type: str=None
    status: str=None
    horse_power: float=None
    data: dict = {}


class CreateFtlRuleSet(BaseModel):
    performed_by_id: str=None
    location_id: str
    location_type: str
    truck_type: str
    process_type: str
    process_unit: str
    process_value: float
    process_currency: str
    status: str




class UpdateFtlRuleSet(BaseModel):
    id: str
    performed_by_id: Optional[str] = None
    performed_by_type: str = None
    location_type: str = None
    truck_type: str = None
    process_type: str = None
    process_unit: str = None
    process_value: float = None
    process_currency: str = None
    status: str = None


class CreateFuelData(BaseModel):
    location_id: str
    location_type: str
    fuel_type: str
    fuel_price: float
    fuel_unit: str
    currency:str

class FtlLineItem(BaseModel):
  code: str
  unit: str
  price: float
  currency: str
  remarks: list[str] = None

class CreateFtlFreightRate(BaseModel):
    rate_sheet_id: str = None
    origin_location_id: str
    destination_location_id: str
    truck_type: str
    commodity: str = None
    importer_exporter_id: str = None
    service_provider_id: str
    performed_by_id: str
    procured_by_id: str
    sourced_by_id: str
    validity_start: datetime
    validity_end: datetime
    truck_body_type: str
    trip_type: str
    transit_time: int
    detention_free_time: int
    minimum_chargeable_weight: float = None
    unit: str = None
    line_items: list[FtlLineItem]
    ftl_freight_rate_request_id: str = None
    performed_by_type: str=None

class Package(BaseModel):
    packing_type: str
    packages_count: int
    package_weight: float = None
    handling_type:  str
    height: float
    length: float
    width: float

class CreateFtlFreightRateRequest(BaseModel):
     source: str
     source_id: str
     performed_by_id: str
     performed_by_org_id: str
     performed_by_type: str
     preferred_freight_rate: float = None
     preferred_freight_rate_currency: str = None
     preferred_detention_free_days: int = None
     preferred_storage_free_days: int = None
     cargo_readiness_date: str = None
     remarks: List[str] = []
     booking_params: dict = {}
     trip_type: str = None
     trucks_count: int = None
     truck_type: str = None
     commodity: str = None
     destination_city_id: str = None
     destination_country_id: str = None
     destination_location_id: str = None
     destination_cluster_id: str = None
     origin_cluster_id: str = None
     origin_country_id: str = None
     origin_city_id: str = None
     origin_location_id: str = None
     load_selection_type: str = None
     free_detention_hours: int = None
     trade_type: str = None
     packages: list[Package] = []

class UpdateFtlFreightRateRequest(BaseModel):
    ftl_freight_rate_request_id: str
    closing_remarks: str
    status: str = None
    remarks: str = None
    
    
class DeleteFtlFreightRateRequest(BaseModel):
    ftl_freight_rate_request_ids: List[str]
    closing_remarks: List[str] = []
    performed_by_id: str = None
    performed_by_type: str = None
    
class CreateFtlFreightRateNotAvailable(BaseModel):
    origin_location_id: str
    origin_cluster_id: str = None
    destination_location_id: str
    destination_cluster_id: str = None
    truck_type: str
    commodity: str = None
    performed_by_id: str = None
    performed_by_type: str = None

class UpdateFtlFreightRatePlatformPrices(BaseModel):
    origin_location_id: str
    destination_location_id: str
    truck_type: str
    commodity_type: str = None
    importer_exporter_id: str = None
    is_line_items_error_messages_present: bool = False


class UpdateFtlFreightRate(BaseModel):
    id: str
    performed_by_id: str
    performed_by_type: str = None
    procured_by_id: str
    sourced_by_id: str
    bulk_operation_id: str = None
    truck_body_type: str
    transit_time: int
    detension_free_time: int
    validity_start: datetime
    validity_end: datetime
    minimum_chargeable_weight: float = None
    line_items: list[FtlLineItem]

class DeleteFtlFreightRate(BaseModel):
    id: str
    performed_by_id: str
    performed_by_type: str = None
    sourced_by_id: str
    procured_by_id: str
    bulk_operation_id: str = None

class CreateFtlFreightRateFeedback(BaseModel):
    source: str
    source_id: str
    performed_by_id: str = None
    performed_by_org_id: str
    performed_by_type: str = None
    rate_id: str
    likes_count: int
    dislikes_count: int
    feedbacks: list[str] = []
    remarks: list[str] = []
    preferred_freight_rate: float = None
    preferred_freight_rate_currency: str = None
    feedback_type: str
    booking_params: dict = {}
    origin_location_id: str = None
    origin_country_id: str = None
    destination_location_id: str = None
    destination_country_id: str = None
    service_provider_id: str = None


class DeleteFtlFreightRateFeedback(BaseModel):
    ftl_freight_rate_feedback_ids: List[str]
    closing_remarks: List[str] = []
    performed_by_id: str = None
    performed_by_type: str = None

    