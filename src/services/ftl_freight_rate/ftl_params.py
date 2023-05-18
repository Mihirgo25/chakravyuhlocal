from pydantic import BaseModel
from peewee import *
    
class CreateFuelData(BaseModel):
    location_id: str 
    location_type: str
    fuel_type: str
    fuel_price: float
    fuel_unit: str
    currency:str
    