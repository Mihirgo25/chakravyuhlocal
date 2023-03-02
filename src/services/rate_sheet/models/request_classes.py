from pydantic import BaseModel, Json

class CreateRateSheet(BaseModel):
    id: str
    service_provider_id: str = None
    service_name: str = None
    file_url: str = None
    comment: str = None
    status: str = None
    converted_files: dict = None
    partner_id: str = None
    agent_id: str = None
    created_at: dict = None
    updated_at: str = None
    serial_id: str = None
    cogo_entity_id: dict = None
