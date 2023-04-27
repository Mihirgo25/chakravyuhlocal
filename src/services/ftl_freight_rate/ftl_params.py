from pydantic import BaseModel
from peewee import *

class CreateTruck(BaseModel):
  performed_by_id: str=None
  performed_by_type: str=None
  name: str= None