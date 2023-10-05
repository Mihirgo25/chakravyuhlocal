from pydantic import BaseModel
from peewee import *

class CreateLclFreightRateJob(BaseModel):
    source: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    origin_port_id: str = None
    destination_port_id: str = None
    service_provider_id: str = None
    commodity: str = None
    rate_type: str = None

class DeleteLclFreightRateJob(BaseModel):
    id: str = None
    closing_remarks: str = None
    data: dict = {}
    rate_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
