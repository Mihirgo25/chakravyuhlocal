from pydantic import BaseModel

class HaulageFreightRate(BaseModel):
    origin_location_id: str
    destination_location_id: str
    commodity: str
    containers_count: int = None
    container_type: str = None
    container_size: str = None
    cargo_weight_per_container: float = None
