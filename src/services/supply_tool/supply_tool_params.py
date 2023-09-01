from pydantic import BaseModel
from peewee import *

class DeleteAirFreightRateJob(BaseModel):
    id: str = None
    closing_remarks: list[str] = []
    rate_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None