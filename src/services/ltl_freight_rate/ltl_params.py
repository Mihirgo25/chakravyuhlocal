from pydantic import BaseModel
from peewee import *

class CreateLtlFreightRateJob(BaseModel):
    source: str = None
    performed_by_id: str = None
    performed_by_type: str = None
    origin_location_id: str = None
    destination_location_id: str = None
    service_provider_id: str = None
    commodity: str = None
    trip_type: str = None
    importer_exporter_id: str = None
    transit_time: str = None
    density_factor: float = None
    rate_type: str = None

class DeleteLtlFreightRateJob(BaseModel):
    id: str = None
    closing_remarks: str = None
    data: dict = {}
    rate_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None
