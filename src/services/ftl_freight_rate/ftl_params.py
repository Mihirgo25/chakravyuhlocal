from pydantic import BaseModel
from peewee import *

class CreateTruck(BaseModel):
  performed_by_id: str=None
  performed_by_type: str=None
  name: str= None
  length: float=None
  breadth: float=None
  height: float=None
  milage: float=None
  milgae_unit: str= None
  capacity: float=None
  capacity_unit: str=None
  vehicle_weight: float=None
  fuel_type: str=None
  truck_company: str=None
  avg_speed: float=None
  no_of_tyres: int=None
  country_id: str=None
  engine_type: str=None
  country: str=None
  axels: int=None
  truck_type: str=None
  body_type: str=None
  status: str=None
  delivery_type: str=None
  horse_power: float=None
  door_width: float=None
  door_height: float=None

class UpdateTruck(BaseModel):
    id: str
    performed_by_id: str=None
    performed_by_type: str=None
    name: str= None