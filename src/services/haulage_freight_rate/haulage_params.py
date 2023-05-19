from pydantic import BaseModel

class HaulageFreightRate(BaseModel):
    origin_location: str
    destination_location: str
    commodity: str
    container_count: int = None
    container_type: str = None
    container_size: str = None
    cargo_weight_per_container: float = None
