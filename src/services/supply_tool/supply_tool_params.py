from pydantic import BaseModel
from datetime import datetime, timedelta, date
from peewee import *

class DeleteFclFreightRateJob(BaseModel):
    id: str = None
    closing_remarks: list[str] = []
    rate_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None