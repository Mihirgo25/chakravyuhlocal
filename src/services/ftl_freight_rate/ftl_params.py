from pydantic import BaseModel
from peewee import *
from typing import Optional

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
  engine_type: str=None
  country_id: str
  axels: int=None
  truck_type: str
  body_type: str=None
  status: str=None
  horse_power: float=None
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
    
class CreateFtlFreightRateJob(BaseModel):
    source: str = None
    source_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    origin_location_id: str = None
    destination_location_id: str = None
    importer_exporter_id: str = None
    service_provider_id: str = None
    truck_type: str = None
    truck_body_type: str = None
    trip_type: str = None
    commodity: str = None
    transit_time: str = None
    detention_free_time: str = None
    unit: str = None
    rate_type: str = None
    
class DeleteFtlFreightRateJob(BaseModel):
    id: str = None
    closing_remarks: list[str] = None
    ftl_freight_rate_feedback_ids: list[str] = None
    ftl_freight_rate_request_ids: list[str] = None
    rate_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
