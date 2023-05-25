from pydantic import BaseModel
from peewee import *
from typing import Optional

class CreateTruck(BaseModel):
  performed_by_id: str
  truck_company: str
  truck_name: str
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

