from pydantic import BaseModel
from peewee import *

class CreateLclFreightRateJob(BaseModel):
    source: str = None
    source_id: str = None
    shipment_id: str = None
    shipment_serial_id: int = None
    performed_by_id: str = None
    performed_by_type: str = None
    origin_port_id: str = None
    destination_port_id: str = None
    service_provider_id: str = None
    commodity: str = None
    is_visible: bool = True
    rate_type: str = None

class DeleteLclFreightRateJob(BaseModel):
    id: str = None
    closing_remarks: list[str] = None
    data: dict = {}
    source_id: str = None
    shipment_id: str = None
    lcl_freight_rate_feedback_ids: list[str] = None
    lcl_freight_rate_request_ids: list[str] = None
    rate_id: str = None
    performed_by_id: str = None
    performed_by_type: str = None

class UpdateLclFreightRateJob(BaseModel):
    id: str
    user_id: str
    performed_by_id: str = None
    performed_by_type: str = None

class UpdateLclFreightRateJobOnRateAddition(BaseModel):
    performed_by_id: str = None
    origin_port_id: str = None
    destination_port_id: str = None
    commodity: str = None
    service_provider_id: str = None