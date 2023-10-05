from pydantic import BaseModel
from peewee import *

class CreateLclCustomsRateJob(BaseModel):
    source: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    location_id: str = None
    service_provider_id: str = None
    importer_exporter_id: str = None
    commodity: str = None
    rate_type: str = None
    trade_type: str = None

class DeleteLclCustomsRateJob(BaseModel):
    id: str = None
    closing_remarks: str = None
    data: dict = {}
    rate_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None