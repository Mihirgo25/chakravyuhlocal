from pydantic import BaseModel
from peewee import *
from typing import Optional



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