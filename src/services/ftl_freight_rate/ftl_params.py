from pydantic import BaseModel
from peewee import *
from typing import Optional

class CreateTruck(BaseModel):
  performed_by_id: str=None
  truck_company: str=None
  truck_name: str=None
  display_name: str=None
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
  country_id: str=None
  axels: int=None
  truck_type: str=None
  body_type: str=None
  status: str=None
  horse_power: float=None
  data: dict = {}

class UpdateTruck(BaseModel):
    id: int
    truck_company: str=None
    truck_name: str=None
    display_name: str=None
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

